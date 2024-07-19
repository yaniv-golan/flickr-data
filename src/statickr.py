import os
import sys
import zipfile
import json
import shutil
import logging
import argparse
from datetime import datetime
import math
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError

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

def check_templates():
    env = Environment(loader=FileSystemLoader('templates'))
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

def render_template(template_name, **kwargs):
    env = Environment(loader=FileSystemLoader('templates'))
    try:
        template = env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound:
        logging.error(f"Template not found: {template_name}")
        raise
    except TemplateSyntaxError as e:
        logging.error(f"Syntax error in template '{template_name}': {str(e)}")
        raise

def create_index_html(dest_folder):
    logging.info("Creating index.html")
    content = render_template('index.html')
    with open(os.path.join(dest_folder, 'index.html'), 'w') as f:
        f.write(content)

def create_photo_page(photo, photo_mapping, dest_folder):
    try:
        photo_id = photo['id']
        title = photo.get('name', 'Untitled')
        img_filename = photo_mapping.get(photo_id, '')
        img_src = f"../images/{img_filename}" if img_filename else ''

        content = render_template('photo.html',
                                  photo=photo,
                                  title=title,
                                  img_src=img_src,
                                  prev_photo=prev_photo,
                                  next_photo=next_photo)

        photo_folder = os.path.join(dest_folder, 'photos')
        os.makedirs(photo_folder, exist_ok=True)
        with open(os.path.join(photo_folder, f'{photo_id}.html'), 'w') as f:
            f.write(content)
    except TemplateSyntaxError as e:
        logging.error(f"Failed to create photo page for photo ID {photo_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error creating photo page for photo ID {photo_id}: {str(e)}")

        
def create_photos_html(data_folder, dest_folder, photo_mapping, oldest_first, enable_paging, photos_per_page):
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
            create_photo_page(photo, photo_mapping, dest_folder)

        content = render_template('photos.html',
                                  photos=page_photos,
                                  page=page,
                                  total_pages=total_pages,
                                  enable_paging=enable_paging)

        with open(os.path.join(photos_folder, f'index{page}.html'), 'w') as f:
            f.write(content)

    if enable_paging:
        shutil.copy(os.path.join(photos_folder, 'index1.html'), os.path.join(photos_folder, 'index.html'))

def create_albums_html(data_folder, dest_folder, photo_mapping, oldest_first):
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
        create_album_page(album, data_folder, albums_folder, photo_mapping, oldest_first)

    content = render_template('albums.html', albums=albums_data['albums'])

    with open(os.path.join(albums_folder, 'index.html'), 'w') as f:
        f.write(content)

def create_album_page(album, data_folder, albums_folder, photo_mapping, oldest_first):
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

    content = render_template('album.html', title=title, photos=album_photos)

    with open(os.path.join(albums_folder, f'{album_id}.html'), 'w') as f:
        f.write(content)

def create_contacts_html(data_folder, dest_folder):
    logging.info("Creating contacts/index.html")
    contacts_file = os.path.join(data_folder, 'contacts_part001.json')
    contacts_folder = os.path.join(dest_folder, 'contacts')
    os.makedirs(contacts_folder, exist_ok=True)

    with open(contacts_file, 'r') as f:
        contacts_data = json.load(f)

    content = render_template('contacts.html', contacts=contacts_data['contacts'])

    with open(os.path.join(contacts_folder, 'index.html'), 'w') as f:
        f.write(content)

def process_flickr_data(source_folder, dest_folder, verbose, oldest_first, enable_paging, photos_per_page):
    try:
        check_templates()
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)

    setup_logging(verbose)
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

        create_index_html(dest_folder)
        create_photos_html(data_folder, dest_folder, photo_mapping, oldest_first, enable_paging, photos_per_page)
        create_albums_html(data_folder, dest_folder, photo_mapping, oldest_first)
        create_contacts_html(data_folder, dest_folder)

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
    args = parser.parse_args()

    try:
        process_flickr_data(args.source_folder, args.destination_folder, args.verbose,
                            args.oldest_first, not args.no_paging, args.photos_per_page)
        print(f"Flickr archive processed and static HTML files created in {args.destination_folder}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
