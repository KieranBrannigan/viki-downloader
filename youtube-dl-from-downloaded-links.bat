:: change filename to the link to the playlist
:: run the batch file
:: %~n0 gets the batch file filename without extension.

youtube-dl --ignore-errors -o "%%(title)s.%%(ext)s" --batch-file="downloaded_links.txt"
PAUSE