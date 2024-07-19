# Technical Documentation for Flickr Data Export

## Overview

This documentation provides a detailed description of the format and contents of the Flickr data export, including zip file names, the structure of the content files within the zip files, and the types of data each file contains. This will enable a developer to build software to process and utilize the provided data effectively.

## How to Obtain Your Flickr Data Export

### Overview

Flickr provides a data export feature that allows users to download their account data, including photos, metadata, comments, and more. This section guides you through the process of requesting and downloading your data export from Flickr.

### Steps to Request Your Data Export

1. **Log in to Your Flickr Account**
   - Go to [Flickr](https://www.flickr.com/) and log in with your account credentials.

2. **Navigate to Your Account Settings**
   - Click on your profile picture in the top right corner of the screen.
   - Select "Settings" from the dropdown menu.

3. **Access Your Data**
   - In the Settings page, click on the "Your Flickr Data" tab.
   - Alternatively, you can directly navigate to [Your Flickr Data](https://www.flickr.com/account/export) (you may need to log in again).

4. **Request Data Export**
   - On the "Your Flickr Data" page, you will see an option to request your Flickr data.
   - Click the "Request My Flickr Data" button.

5. **Wait for Data Preparation**
   - Flickr will begin preparing your data for download. This process may take some time depending on the amount of data in your account.
   - You will receive an email notification once your data is ready for download.

6. **Download Your Data**
   - After receiving the notification email, return to the "Your Flickr Data" page.
   - You will see download links for your data export files.
   - Click on each link to download the zip files containing your data.

### Relevant Flickr Documentation

For more detailed information and troubleshooting, refer to the official Flickr documentation and support pages:

- [Flickr Help Center](https://help.flickr.com/)
- [How to Request Your Flickr Data](https://help.flickr.com/en_us/requesting-your-flickr-data-rJeqVk9Wx)
- [Flickr Data Export FAQ](https://help.flickr.com/en_us/data-export-faqs-HkNJr1viV)

These resources provide additional instructions and support for users who need assistance with the data export process.

## JSON Schemas

To help with validating and understanding the structure of the JSON data files, JSON Schemas are provided. These schemas describe the expected structure and content of each JSON file in the Flickr data export.

The schemas are available in the `docs/schemas` directory:

## JSON Schemas

To help with validating and understanding the structure of the JSON data files, JSON Schemas are provided. These schemas describe the expected structure and content of each JSON file in the Flickr data export.

The schemas are available in the `docs/schemas` directory:

- [account_profile.schema.json](schemas/account_profile.schema.json)
- [account_testimonials.schema.json](schemas/account_testimonials.schema.json)
- [albums.schema.json](schemas/albums.schema.json)
- [contacts_part001.schema.json](schemas/contacts_part001.schema.json)
  - Note: `contacts_part###.json` indicates the sequence of contact parts.
- [faves_part001.schema.json](schemas/faves_part001.schema.json)
  - Note: `faves_part###.json` indicates the sequence of favorite parts.
- [followers_part001.schema.json](schemas/followers_part001.schema.json)
  - Note: `followers_part###.json` indicates the sequence of follower parts.
- [galleries.schema.json](schemas/galleries.schema.json)
- [group_discussions.schema.json](schemas/group_discussions.schema.json)
- [photo_[ID].schema.json](schemas/photo_[ID].schema.json)
  - Note: `photo_[ID].json` should be replaced with the actual photo ID.
- [photos_comments_part001.schema.json](schemas/photos_comments_part001.schema.json)
  - Note: `photos_comments_part###.json` indicates the sequence of photo comment parts.
- [received_flickrmail_part001.schema.json](schemas/received_flickrmail_part001.schema.json)
  - Note: `received_flickrmail_part###.json` indicates the sequence of received Flickr mail parts.
- [sent_flickrmail_part001.schema.json](schemas/sent_flickrmail_part001.schema.json)
  - Note: `sent_flickrmail_part###.json` indicates the sequence of sent Flickr mail parts.
- [sets_comments_part001.schema.json](schemas/sets_comments_part001.schema.json)
  - Note: `sets_comments_part###.json` indicates the sequence of set comment parts.

Refer to these schemas to ensure that your JSON data files conform to the expected structure and format.

## Zip File Structure

The data export from Flickr is provided in multiple zip files. Each zip file contains various JSON files that hold different types of information related to your Flickr account.

## Zip File Names

The zip files are typically named as follows:

1. **Metadata File**:
   - `nnnnnnnnnnnn_mmmmmmmm_part1.zip`: Contains JSON files with metadata. Here, `nnnnnnnnnnnn` is a long number, and `mmmmmmmm` is a long hexadecimal number.

2. **Image Files**:
   - `data-download-1.zip`: Contains image files.
   - `data-download-2.zip`: Contains image files.
   - (and so on, depending on the number of images).

## Content File Names and Structures

### Metadata Zip File (nnnnnnnnnnnn_mmmmmmmm_part1.zip)

1. **account_profile.json**
    - **Description**: Contains information about the account profile.
    - **Structure**:
      ```json
      {
        "real_name": "User Name",
        "joined_date": "2005-08-31",
        "description": "Flickr: https://www.instagram.com/username/",
        "country": "Country",
        "email": "user@example.com",
        "profile_url": "https://www.flickr.com/people/username/",
        "nsid": "12345678@N00",
        "screen_name": "UserScreenName",
        "is_pro": true,
        "showcase_photos": ["123456789", "987654321"],
        "settings": {
          "privacy": "public",
          "sharing": {
            "facebook": true,
            "twitter": false
          }
        },
        "stats": {
          "views": 12345,
          "tags_count": 678,
          "geotags_count": 90,
          "faves_count": 123,
          "groups_count": 45,
          "comments_count": 67
        }
      }
      ```

2. **account_testimonials.json**
    - **Description**: Contains testimonials given and received.
    - **Structure**:
      ```json
      {
        "testimonials_given": [
          {
            "user": "user123",
            "comment": "Great photographer!",
            "url": "https://www.flickr.com/people/user123/"
          }
        ],
        "testimonials_received": [
          {
            "user": "user456",
            "comment": "Amazing work!",
            "url": "https://www.flickr.com/people/user456/"
          }
        ]
      }
      ```

3. **albums.json**
    - **Description**: Contains information about photo albums.
    - **Structure**:
      ```json
      {
        "albums": [
          {
            "id": "album123",
            "title": "Vacation",
            "description": "Photos from my vacation.",
            "photo_count": 100,
            "view_count": 200,
            "created": "YYYY-MM-DD HH:MM:SS",
            "last_updated": "YYYY-MM-DD HH:MM:SS",
            "cover_photo": "cover_photo_id",
            "photos": ["photo1", "photo2"]
          }
        ]
      }
      ```

4. **contacts_part001.json**
    - **Description**: Contains a list of contacts.
    - **Structure**:
      ```json
      {
        "contacts": {
          "contact_name": "https://www.flickr.com/people/contact_url/",
          ...
        }
      }
      ```

5. **faves_part001.json**
    - **Description**: Contains a list of favorite photos.
    - **Structure**:
      ```json
      {
        "favorites": [
          {
            "photo_id": "123456",
            "photo_url": "https://www.flickr.com/photos/photo_url/"
          }
        ]
      }
      ```

6. **followers_part001.json**
    - **Description**: Contains a list of followers.
    - **Structure**:
      ```json
      {
        "followers": {
          "follower_name": "https://www.flickr.com/people/follower_url/",
          ...
        }
      }
      ```

7. **galleries.json**
    - **Description**: Contains information about galleries.
    - **Structure**:
      ```json
      {
        "galleries": [
          {
            "id": "gallery123",
            "title": "My Gallery",
            "description": "A collection of my best photos.",
            "photo_count": 50,
            "view_count": 100,
            "photos": ["photo1", "photo2"]
          }
        ]
      }
      ```

8. **group_discussions.json**
    - **Description**: Contains information about group discussions.
    - **Structure**:
      ```json
      {
        "group_discussions": [
          {
            "type": "topic",
            "subject": "Discussion Topic",
            "url": "https://www.flickr.com/groups/group_id/discuss/12345/",
            "message": "This is a discussion message.",
            "date_create": "2020-01-01T00:00:00Z"
          }
        ]
      }
      ```

9. **photo_[ID].json**
    - **Description**: Contains metadata for individual photos.
    - **Structure**:
      ```json
      {
        "id": "photo_id",
        "name": "photo_name",
        "description": "photo_description",
        "count_views": 123,
        "count_faves": 10,
        "count_comments": 5,
        "date_taken": "YYYY-MM-DD HH:MM:SS",
        "tags": ["tag1", "tag2"],
        "geo": {
          "latitude": "lat_value",
          "longitude": "lon_value",
          "accuracy": "accuracy_value"
        },
        "groups": [
          {
            "id": "group_id",
            "name": "Group Name",
            "url": "https://www.flickr.com/groups/group_url/"
          }
        ],
        "albums": ["album_id1", "album_id2"],
        "privacy": "privacy_status",
        "comment_permissions": "comment_permissions",
        "tagging_permissions": "tagging_permissions",
        "safety": "safety_status",
        "comments": [
          {
            "user": "comment_user",
            "message": "comment_message",
            "date_create": "YYYY-MM-DD HH:MM:SS"
          }
        ]
      }
      ```

10. **photos_comments_part001.json** and **photos_comments_part002.json**
    - **Description**: Contains comments on photos.
    - **Structure**:
      ```json
      {
        "comments": [
          {
            "photo_id": "photo_id",
            "comment_id": "comment_id",
            "user": "comment_user",
            "message": "comment_message",
            "date_create": "YYYY-MM-DD HH:MM:SS"
          }
        ]
      }
      ```

11. **received_flickrmail_part001.json**
    - **Description**: Contains received Flickr mail messages.
    - **Structure**:
      ```json
      {
        "flickrmail": [
          {
            "id": "mail_id",
            "from_user_id": "sender_id",
            "to_user_id": "recipient_id",
            "subject": "mail_subject",
            "message": "mail_body",
            "date_sent": "YYYY-MM-DD HH:MM:SS",
            "date_deleted": "YYYY-MM-DD HH:MM:SS"
          }
        ]
      }
      ```

12. **sent_flickrmail_part001.json**
    - **Description**: Contains sent Flickr mail messages.
    - **Structure**:
      ```json
      {
        "flickrmail": [
          {
            "id": "mail_id",
            "from_user_id": "sender_id",
            "to_user_id": "recipient_id",
            "to_user_name": "recipient_name",
            "subject": "mail_subject",
            "message": "mail_body",
            "date_sent": "YYYY-MM-DD HH:MM:SS",
            "date_deleted": "YYYY-MM-DD HH:MM:SS"
          }
        ]
      }
      ```

13. **sets_comments_part001.json**
    - **Description**: Contains comments on photo sets/albums.
    - **Structure**:
      ```json
      {
        "comments": [
          {
            "set_id": "set_id",
            "comment_id": "comment_id",
            "user": "comment_user",
            "message": "comment_message",
            "date_create": "YYYY-MM-DD HH:MM:SS"
          }
        ]
      }
      ```

### Image Zip File(s)

1. **File name format**: `data-download-1.zip`, `data-download-2.zip`, etc.
    - **Contents**:
      - Original image files.
      - File names include the original file name and the Flickr photo ID.
      - Various image formats (e.g., jpg, png) are preserved.

### Summary of the Data

- **Account Information**: Profile details, account settings, testimonials, and statistical data.
- **Photos**: Metadata including photo ID, name, description, views, favorites, comments, date taken, tags, geolocation, privacy settings, and group/album associations.
- **Albums and Galleries**: Information about the collections of photos.
- **Contacts and Followers**: Lists of contacts and followers with URLs to their profiles.
- **Group Discussions**: Details about group discussions the user has participated in.
- **Comments**: Comments made on photos.
- **Flickr Mail**: Messages received and sent through Flickr mail.

### Additional Notes

- Some JSON files may be split into multiple parts (e.g., `contacts_part001.json`, `followers_part001.json`) if the data is extensive.
- The number of image zip files depends on the total size of the user's photo collection.
- All dates in the JSON files are typically in the format "YYYY-MM-DD HH:MM:SS".
- The metadata zip file contains a comprehensive record of the user's Flickr activity, including photos, social interactions, and account settings.
- Privacy settings and permissions for each photo are included in the individual photo JSON files.
- The export includes both public and private data associated with the user's account.

### Developer Notes

1. **Data Parsing**: Ensure JSON parsing is robust to handle any variations or unexpected data structures.
2. **Data Privacy**: Pay attention to privacy settings and permissions when displaying or processing data.
3. **Licenses**: Respect the license information provided with each photo.

