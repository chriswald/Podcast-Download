import urllib.request
import xml.etree.ElementTree as ET
import mimetypes
import os

fname = "config.xml"

config = ET.parse(fname).getroot()
outputDirectory = config.find("outputDir").text

for feed in config.find("feeds").findall("feed"):
	feedUrl = feed.find("url").text
	feedName = feed.get("name")

	# Configure the filters that will be used to skip downloading
	# certain episodes
	feedExcludeFilters = []
	if (feed.find("filters") != None and feed.find("filters").find("filter") != None):
		feedExcludeFilters = [exclude.text for exclude in feed.find("filters").findall("filter")]

	# Download the podcast's RSS feed
	response = urllib.request.urlopen(feedUrl)
	rssXml = response.read()
	xmlRoot = ET.fromstring(rssXml)
	xmlChannelNode = xmlRoot.find("channel")
	
	for episode in xmlChannelNode.findall("item"):
		episodeTitle = episode.find("title").text

		# If there are any filters then see if any of the filters
		# exist in the episode title
		if len(feedExcludeFilters) > 0:
			if any(exclude.lower() in episodeTitle.lower() for exclude in feedExcludeFilters): continue

		episodeUrl = episode.find("enclosure").get("url")
		episodeMimeType = episode.find("enclosure").get("type")
		episodeFileExtension = mimetypes.guess_extension(episodeMimeType)
		episodeFileName = episodeTitle + "." + episodeFileExtension
		episodeFileName = episodeFileName.replace(":", "")
		fullOutputPath = os.path.join(outputDirectory, feedName)
		fullOutputPath = os.path.abspath(fullOutputPath)

		if (not os.path.exists(fullOutputPath)):
			os.makedirs(fullOutputPath)

		fullOutputPath = os.path.join(fullOutputPath, episodeFileName)

		if (not os.path.exists(fullOutputPath)):
			urllib.request.urlretrieve(episodeUrl, fullOutputPath)
