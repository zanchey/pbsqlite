# pbsqlite - Import Australian PBS data into an SQLite database

> pbs: hey here is our database as some text files
> 
> developers: ok cool we can turn that into a database
> 
> pbs: uh all the files use different delimiters though
> 
> dev: well maybe you could tidy it up, a bunch of them change delimiters halfway through?
> 
> pbs: no but here it is as a giant XML document
> 
> dev: ok? we'll just keep using the text files though, but any chance the number of columns in the header could match the file?
> 
> pbs: now here it is as some more complicated XML 🙃
> 
> dev: I mean sure, but we'll still just use the text files, unless you want to give us a database directly?
> 
> pbs: no but we will write an API to send the tables over JSON 🙃🙃🙃
>
> dev: well that just sounds like CSV with extra steps
>
> pbs: ok fair enough, we're making a zipfile full of CSVs available
>
> dev: come on pal I just finished making the API client

You just want to be able to SELECT a drug? You can use these scripts to get an SQLite database from the PBS data. Text extracts are supported through the import-text script, and the public API through import-API. The CSV downloads from the API are not yet supported.

The data model is largely to what comes out of the text extracts / API. Some examples are included, or you can transform it into something more complex.

SQLite creates automatic indexes for common queries, and the dataset is so small that most queries should complete in tens of milliseconds.

## Releases

You can download pre-built databases from [pbsqlite releases on GitHub](https://github.com/zanchey/pbsqlite/releases/).

## Usage (API)

1. Create a new virtual environment with sqlite-utils installed; pipenv is recommended (run `pipenv sync`).
1. Run `pipenv run python3 import-api.py`. This will download the most recent schedule.
1. Use your new `pbs-2024-12-01.sqlite3` database with the world's most popular database software.

## Usage (text extracts)

The API client uses [sqlite-utils](https://sqlite-utils.datasette.io/) as a dependency.

1. Download the text extract Zip file for the month (eg `2021-05-01-v3extracts.zip`).
1. Run `./import-text.py 2021-05-01-v3extracts.zip`.
1. Use your new `pbs-20210501.sqlite3` database with the world's most popular database software.

## License

Licensed under the MIT license; see [LICENSE.txt](LICENSE.txt) for more.

## Author

David Adam (https://github.com/zanchey) wrote this, because anything is better than parsing XML.
