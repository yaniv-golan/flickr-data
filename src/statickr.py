import os
import sys
import zipfile
import json
import shutil
import logging
import argparse
from email.utils import formatdate
import math
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError
import requests
from bs4 import BeautifulSoup
import time
import re

# List of required templates
REQUIRED_TEMPLATES = [
    'index.html',
    'photo.html',
    'photos.html',
    'albums.html',
    'album.html',
    'contacts.html'
]

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

GENERIC_AVATAR_URL = "https://www.flickr.com/images/buddyicon.gif"

def get_flickr_buddy_icon_url(flickr_url, last_fetch_times):
    try:
        headers = {}
        if flickr_url in last_fetch_times:
            headers['If-Modified-Since'] = last_fetch_times[flickr_url]

        response = requests.get(flickr_url, headers=headers)
        if response.status_code == 304:  # Not Modified
            logging.debug(f"Avatar for {flickr_url} not modified since last fetch")
            return None, False

        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        avatar_div = soup.find('div', class_=['avatar', 'person'])
        if avatar_div:
            style = avatar_div.get('style')
            if style:
                match = re.search(r'url\((.*?)\)', style)
                if match:
                    avatar_url = match.group(1).strip("'\"")
                    if avatar_url.startswith('//'):
                        avatar_url = 'https:' + avatar_url
                    logging.debug(f"Found avatar URL for {flickr_url}: {avatar_url}")
                    return avatar_url, True

        logging.debug(f"No avatar found for {flickr_url}")
        return None, False

    except requests.RequestException as e:
        logging.error(f"Error fetching the Flickr page: {e}")
        return None, False
    finally:
        time.sleep(1)  # Add a 1-second delay after each request, even if it fails

def get_templates_env():
    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the templates directory
    templates_dir = os.path.join(script_dir, 'templates')
    
    # Setup the Jinja2 environment to load templates from the correct directory
    env = Environment(loader=FileSystemLoader(templates_dir))
    return env

def check_templates(env):
    missing_templates = []
    for template in REQUIRED_TEMPLATES:
        try:
            env.get_template(template)
        except TemplateNotFound:
            missing_templates.append(template)
    
    if missing_templates:
        raise FileNotFoundError(f"The following template files are missing: {', '.join(missing_templates)}")

def extract_zip_files(source_folder, dest_folder):
    logging.info(f"Extracting ZIP files from {source_folder} to {dest_folder}")
    for file in os.listdir(source_folder):
        if file.endswith('.zip'):
            logging.debug(f"Extracting {file}")
            with zipfile.ZipFile(os.path.join(source_folder, file), 'r') as zip_ref:
                zip_ref.extractall(dest_folder)

def get_photo_filename_mapping(images_folder):
    logging.info("Creating photo filename mapping")
    mapping = {}
    for filename in os.listdir(images_folder):
        if filename.endswith('_o.jpg'):
            parts = filename.split('_')
            if len(parts) >= 2:
                photo_id = parts[-2]  # The ID is the second-to-last part
                mapping[photo_id] = filename
    logging.debug(f"Found {len(mapping)} photo mappings")
    return mapping

def render_template(env, template_name, **kwargs):
    try:
        template = env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound:
        logging.error(f"Template not found: {template_name}")
        raise
    except TemplateSyntaxError as e:
        logging.error(f"Syntax error in template '{template_name}': {str(e)}")
        raise

def create_index_html(env, dest_folder):
    logging.info("Creating index.html")
    content = render_template(env, 'index.html')
    with open(os.path.join(dest_folder, 'index.html'), 'w') as f:
        f.write(content)

def create_photo_page(env, photo, photo_mapping, dest_folder, user_avatar, user_name, albums):
    try:
        photo_id = photo['id']
        title = photo.get('name', 'Untitled')
        description = photo.get('description', '')
        count_views = photo.get('count_views', 0)
        count_faves = photo.get('count_faves', 0)
        count_comments = photo.get('count_comments', 0)
        exif_data = photo.get('exif_data', {})
        groups = photo.get('groups', [])
        tags = photo.get('tags', [])

        img_filename = photo_mapping.get(photo_id, '')
        img_src = f"../images/{img_filename}" if img_filename else ''

        # Update the albums list to include icons
        for album in albums:
            album['icon'] = f"../images/{album['cover_photo_filename']}" if album.get('cover_photo_filename') else '/images/album_cover.jpg'

        content = render_template(env, 'photo.html',
                                  photo={
                                      'id': photo_id,
                                      'name': title,
                                      'description': description,
                                      'count_views': count_views,
                                      'count_faves': count_faves,
                                      'count_comments': count_comments,
                                      'exif_data': exif_data,
                                      'groups': groups,
                                      'tags': tags
                                  },
                                  title=title,
                                  img_src=img_src,
                                  user_avatar=user_avatar,
                                  user_name=user_name,
                                  albums=albums)

        photo_folder = os.path.join(dest_folder, 'photos')
        os.makedirs(photo_folder, exist_ok=True)
        with open(os.path.join(photo_folder, f'{photo_id}.html'), 'w') as f:
            f.write(content)
    except TemplateSyntaxError as e:
        logging.error(f"Failed to create photo page for photo ID {photo_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error creating photo page for photo ID {photo_id}: {str(e)}")

def create_photos_html(env, data_folder, dest_folder, photo_mapping, oldest_first, enable_paging, photos_per_page, user_avatar, user_name, albums):
    logging.info("Creating photos/index.html")
    photos = []
    photos_folder = os.path.join(dest_folder, 'photos')
    os.makedirs(photos_folder, exist_ok=True)

    for file in os.listdir(data_folder):
        if file.startswith('photo_') and file.endswith('.json'):
            with open(os.path.join(data_folder, file), 'r') as f:
                photo_data = json.load(f)
                photos.append(photo_data)

    # Sort photos by date
    photos.sort(key=lambda x: x.get('date_taken', ''), reverse=not oldest_first)

    total_pages = math.ceil(len(photos) / photos_per_page) if enable_paging else 1

    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * photos_per_page
        end_idx = start_idx + photos_per_page
        page_photos = photos[start_idx:end_idx] if enable_paging else photos

        for photo in page_photos:
            photo['img_src'] = f"../images/{photo_mapping.get(photo['id'], '')}"
            create_photo_page(env, photo, photo_mapping, dest_folder, user_avatar, user_name, albums)

        content = render_template(env, 'photos.html',
                                  photos=page_photos,
                                  page=page,
                                  total_pages=total_pages,
                                  enable_paging=enable_paging)

        with open(os.path.join(photos_folder, f'index{page}.html'), 'w') as f:
            f.write(content)

    if enable_paging:
        shutil.copy(os.path.join(photos_folder, 'index1.html'), os.path.join(photos_folder, 'index.html'))

def create_albums_html(env, data_folder, dest_folder, photo_mapping, oldest_first):
    logging.info("Creating albums/index.html and individual album pages")
    albums_file = os.path.join(data_folder, 'albums.json')
    albums_folder = os.path.join(dest_folder, 'albums')
    os.makedirs(albums_folder, exist_ok=True)

    with open(albums_file, 'r') as f:
        albums_data = json.load(f)

    # Sort albums by date
    albums_data['albums'].sort(key=lambda x: x.get('created', ''), reverse=not oldest_first)

    for album in albums_data['albums']:
        album['cover_photo_filename'] = photo_mapping.get(album.get('cover_photo', '').split('/')[-1], '')
        create_album_page(env, album, data_folder, albums_folder, photo_mapping, oldest_first)

    content = render_template(env, 'albums.html', albums=albums_data['albums'])

    with open(os.path.join(albums_folder, 'index.html'), 'w') as f:
        f.write(content)

def create_album_page(env, album, data_folder, albums_folder, photo_mapping, oldest_first):
    album_id = album['id']
    title = album.get('title', 'Untitled Album')
    photos = album.get('photos', [])

    logging.debug(f"Creating album page for '{title}' (ID: {album_id})")

    album_photos = []
    for photo_id in photos:
        photo_file = os.path.join(data_folder, f'photo_{photo_id}.json')
        if os.path.exists(photo_file):
            with open(photo_file, 'r') as f:
                photo_data = json.load(f)
                photo_data['img_src'] = f"../images/{photo_mapping.get(photo_id, '')}"
                album_photos.append(photo_data)

    # Sort photos by date
    album_photos.sort(key=lambda x: x.get('date_taken', ''), reverse=not oldest_first)

    content = render_template(env, 'album.html', title=title, photos=album_photos)

    with open(os.path.join(albums_folder, f'{album_id}.html'), 'w') as f:
        f.write(content)

def create_safe_filename(name):
    # Remove any non-alphanumeric characters and replace spaces with underscores
    safe_name = re.sub(r'[^\w\-_\. ]', '', name)
    safe_name = safe_name.replace(' ', '_')
    # Limit the length of the filename
    return safe_name[:50]  # Limiting to 50 characters

def create_contacts_html(env, data_folder, dest_folder, fetch_avatars, skip_existing_avatars):
    logging.info("Creating contacts/index.html")
    contacts_file = os.path.join(data_folder, 'contacts_part001.json')
    contacts_folder = os.path.join(dest_folder, 'contacts')
    avatars_folder = os.path.join(dest_folder, 'avatars')
    os.makedirs(contacts_folder, exist_ok=True)
    os.makedirs(avatars_folder, exist_ok=True)

    # Load the last fetch times
    last_fetch_file = os.path.join(avatars_folder, 'last_fetch.json')
    if os.path.exists(last_fetch_file):
        with open(last_fetch_file, 'r') as f:
            last_fetch_times = json.load(f)
    else:
        last_fetch_times = {}

    with open(contacts_file, 'r') as f:
        contacts_data = json.load(f)

    if not isinstance(contacts_data, dict) or 'contacts' not in contacts_data:
        raise ValueError(f"Unexpected structure in {contacts_file}: expected a dictionary with a 'contacts' key")

    contacts = contacts_data['contacts']
    updated_contacts = []

    for name, url in contacts.items():
        avatar_url = None

        safe_name = create_safe_filename(name)
        avatar_filename = f"{safe_name}.jpg"
        avatar_path = os.path.join(avatars_folder, avatar_filename)

        if skip_existing_avatars and os.path.exists(avatar_path):
            logging.debug(f"Skipping fetch for existing avatar: {avatar_path}")
            avatar_relative_path = os.path.relpath(avatar_path, contacts_folder)
        else:
            if fetch_avatars:
                avatar_url, modified = get_flickr_buddy_icon_url(url, last_fetch_times)
            else:
                modified = False

            if avatar_url and modified:
                try:
                    response = requests.get(avatar_url)
                    response.raise_for_status()
                    with open(avatar_path, 'wb') as f:
                        f.write(response.content)
                    logging.debug(f"Successfully saved avatar to {avatar_path}")
                    last_fetch_times[url] = formatdate(timeval=None, localtime=False, usegmt=True)
                    avatar_relative_path = os.path.relpath(avatar_path, contacts_folder)
                except requests.RequestException as e:
                    logging.error(f"Failed to fetch avatar for {name}: {e}")
                    avatar_relative_path = os.path.relpath(GENERIC_AVATAR_URL, contacts_folder)
                except IOError as e:
                    logging.error(f"Failed to save avatar for {name}: {e}")
                    avatar_relative_path = os.path.relpath(GENERIC_AVATAR_URL, contacts_folder)
            else:
                logging.debug(f"No avatar URL found or not modified for {name}, using generic avatar")
                avatar_relative_path = os.path.relpath(GENERIC_AVATAR_URL, contacts_folder)

        updated_contacts.append({
            "name": name,
            "url": url,
            "avatar": avatar_relative_path
        })

    # Save the updated last fetch times
    with open(last_fetch_file, 'w') as f:
        json.dump(last_fetch_times, f)

    content = render_template(env, 'contacts.html', contacts=updated_contacts)

    with open(os.path.join(contacts_folder, 'index.html'), 'w') as f:
        f.write(content)


def process_flickr_data(source_folder, dest_folder, verbose, oldest_first, enable_paging, photos_per_page, fetch_avatars, skip_existing_avatars):
    setup_logging(verbose)
    env = get_templates_env()
    
    try:
        check_templates(env)
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)

    logging.info(f"Processing Flickr data from {source_folder} to {dest_folder}")

    data_folder = os.path.join(dest_folder, 'data')
    images_folder = os.path.join(dest_folder, 'images')
    
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)

    try:
        extract_zip_files(source_folder, data_folder)
        
        logging.info("Moving image files to the images folder")
        for file in os.listdir(data_folder):
            if file.endswith('.jpg') or file.endswith('.png'):
                shutil.move(os.path.join(data_folder, file), os.path.join(images_folder, file))

        photo_mapping = get_photo_filename_mapping(images_folder)

        # Extract user avatar and name from account_profile.json
        account_profile_file = os.path.join(data_folder, 'account_profile.json')
        with open(account_profile_file, 'r') as f:
            account_profile = json.load(f)
            user_avatar = account_profile.get('avatar', GENERIC_AVATAR_URL)
            user_name = account_profile.get('real_name', 'Unknown User')

        # Extract albums data from albums.json
        albums_file = os.path.join(data_folder, 'albums.json')
        with open(albums_file, 'r') as f:
            albums_data = json.load(f)
            albums = albums_data.get('albums', [])

        create_index_html(env, dest_folder)
        create_photos_html(env, data_folder, dest_folder, photo_mapping, oldest_first, enable_paging, photos_per_page, user_avatar, user_name, albums)
        create_albums_html(env, data_folder, dest_folder, photo_mapping, oldest_first)
        create_contacts_html(env, data_folder, dest_folder, fetch_avatars, skip_existing_avatars)

        logging.info("Flickr archive processing complete")
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate static Flickr archive")
    parser.add_argument("source_folder", help="Folder containing Flickr data ZIP files")
    parser.add_argument("destination_folder", help="Folder to store generated static files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--oldest-first", action="store_true", help="Sort photos and albums oldest first")
    parser.add_argument("--no-paging", action="store_true", help="Disable paging for photos")
    parser.add_argument("--photos-per-page", type=int, default=20, help="Number of photos per page (default: 20)")
    parser.add_argument("--no-fetch-avatars", action="store_true", help="Disable fetching of user avatars")
    parser.add_argument("--skip-existing-avatars", action="store_true", help="Skip fetching avatars if they already exist")
    args = parser.parse_args()

    try:
        process_flickr_data(
            source_folder=args.source_folder,
            dest_folder=args.destination_folder,
            verbose=args.verbose,
            oldest_first=args.oldest_first,
            enable_paging=not args.no_paging,
            photos_per_page=args.photos_per_page,
            fetch_avatars=not args.no_fetch_avatars,
            skip_existing_avatars=args.skip_existing_avatars
        )
        print(f"Flickr archive processed and static HTML files created in {args.destination_folder}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
