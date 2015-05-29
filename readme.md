# Parity Scraper

## Introduction

When migrating a web service from one platform to another, I found myself wanting to make sure that the old and new services provided the same response for a range of different inputs. Some time later, I found myself needing to do this again, when some underlying components I depended on changed.

Over time, I found myself tweaking my script to cope with different scenarios, and so decided to put it under source control, and share incase anyone else finds it useful.

## Usage

When you run the parity.py script, it looks for a file named parity.ini, from which to load settings. You may optionally specify an ini file on the command line (useful for maintaining multiple sets of settings).

Amongst the most important settings are the control and treatment URL formats, and the file from which to load queries. The URL format strings should have markers like {0}, {1}, etc to indicate parameter placeholders. Each line in the query file should have a corresponding number of tab-separated values.

For each line in the file, a control and treatment URL is constructed by replacing the placeholders with the values for that line. Both URLs are then queried, and the responses compared. If differences are encountered, the responses are saved in the 'output' directory, and the Diff program (expected to be in the path) is invoked to identify the exact differences.

## Configuration

The ini file can contain a number of settings, to control how Parity Scraper operates.

### General Settings

These are found within the [Settings] section.

* ControlUrlFormat - As described above, using {0}, {1}, etc, for placeholders.
* TreatmentUrlFormat - As described above, using {0}, {1}, etc, for placeholders.
* PostDataFormat - Optional; if present, the request will be a 'post' instead of a 'get', and this will be send as the body. This value may optionally contain placeholders, like the control/treatment URLs.
* QueryFilename - The path to the file from which to load the query parameters.

### Headers

HTTP headers can be specified in the [Headers] section. Each key/value pair corresponds to the key/value for the HTTP header.

### Ignore Patterns

Sometimes, you want to ignore certain parts of the response, such as unique IDs and timestamps, which will never match. You can specify a list of regular expressions in the [Ignore] section - these will be applied in turn, and the matches stripped from the response before comparison.

It doesn't actually matter what the keys in this section are - the values are the regular expressions. I personally just use numbers.

