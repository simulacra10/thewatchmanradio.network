import os
import aiohttp
import asyncio
import xml.etree.ElementTree as ET

async def download_file(session, url, directory, file_name):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                total_size = response.content_length
                downloaded = 0
                chunk_size = 65536  # Read in chunks of 64KB

                with open(os.path.join(directory, file_name), 'wb') as file:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        file.write(chunk)
                        downloaded += len(chunk)
                        percentage = (downloaded / total_size) * 100
                        print(f"Downloading {file_name}: {percentage:.2f}% complete", end='\r')
                print()  # Move to next line after download completes
                return file_name
            else:
                print(f"Failed to download {file_name}: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")
        return None

async def download_files(date, day_of_week):
    base_url = "http://affiliates.infowars.com/show-segs/"
    directory = f"{date}_files"
    os.makedirs(directory, exist_ok=True)

    playlist_path = os.path.join(directory, f"{date}_playlist.xspf")
    playlist = ET.Element('playlist', version="1", xmlns="http://xspf.org/ns/0/")
    track_list = ET.SubElement(playlist, 'trackList')

    # Function to add station ID track
    def add_station_id_track():
        track = ET.SubElement(track_list, 'track')
        location = ET.SubElement(track, 'location')
        location.text = "twrn-station-ID.mp3"
        title = ET.SubElement(track, 'title')
        title.text = "twrn-station-ID"

    # Add station ID track at the beginning
    add_station_id_track()

    tasks = []
    async with aiohttp.ClientSession() as session:
        for hr in range(1, 5):
            for seg in range(1, 6):
                file_name = f"{date}_{day_of_week}_ALEX-HR{hr}-SEG{seg}.mp3"
                full_url = f"{base_url}{file_name}"
                task = asyncio.create_task(download_file(session, full_url, directory, file_name))
                tasks.append(task)

                # Wait for task completion before adding the station ID track as a bookend
                await asyncio.gather(*tasks)
                tasks = []

                # Add the downloaded track and then the station ID track as a bookend
                track = ET.SubElement(track_list, 'track')
                location = ET.SubElement(track, 'location')
                location.text = file_name
                title = ET.SubElement(track, 'title')
                title.text = file_name

                # Add station ID track after each song
                add_station_id_track()

    # Write out the playlist to an XSPF file
    tree = ET.ElementTree(playlist)
    tree.write(playlist_path, encoding='utf-8', xml_declaration=True)
    print(f"All files downloaded to {directory}.")
    print(f"Playlist file created at {playlist_path}.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <date> <day of week>")
        print("Example: python script.py 20240510 Fri")
        sys.exit(1)
    date = sys.argv[1]
    dow = sys.argv[2]
    asyncio.run(download_files(date, dow))
