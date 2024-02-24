# Use the standard Python 3.10 image
FROM python:3.10

# Install yt-dlp dependencies and yt-dlp itself
# Adding necessary packages including ffmpeg
RUN apt-get update && apt-get install -y --fix-missing \
    ffmpeg \
    dos2unix \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir yt-dlp ytdlp-brighteon>=2023.10.3

# Set the working directory in the container
WORKDIR /host_dir

# Build the entrypoint script in the container.
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'yt-dlp "$@"' >> /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to use /bin/sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
