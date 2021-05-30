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

You just want to be able to SELECT a drug? You can use these scripts to get an SQLite database from the PBS data. Text extracts are supported at present, with API integration planned.

The data model is largely to what comes out of the text extracts. Some examples are included, or you can transform it into something more complex.

SQLite creates automatic indexes for common queries, and the dataset is so small that most queries should complete in tens of milliseconds.

## Usage

1. Download the text extract Zip file for the month (eg `2021-05-01-v3extracts.zip`).
1. Run `./import-text.py 2021-05-01-v3extracts.zip`.
1. Use your new `pbs-20210501.sqlite3` database with the world's most popular database software.

## License

Licensed under the MIT license; see [LICENSE.txt](LICENSE.txt) for more.

## Author

David Adam (https://github.com/zanchey) wrote this, because anything is better than parsing XML.