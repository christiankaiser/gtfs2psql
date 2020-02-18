# gtfs2psql

Reads a GTFS feed into SQL code for importing in a PostgreSQL+PostGIS database.

## Usage

```bash
python gtfs2psql.py [--schema <schema>] [--prefix <table-prefix>] gtfs > gtfs.sql
```

where the arguments are:

- `--schema` takes the name of the database schema. Defaults to `public`.
- `--prefix` is an optional prefix that will be added in front of every table name. By default, one table is created for each file in the GTFS feed.
- `gtfs` is the path to the unzipped GTFS feed.


The output can be redirected to a SQL file as illustrated above. It also can be fed directly into a PostgreSQL database using the pipe operator, e.g.

```bash
python gtfs2psql.py /path/to/gtfs | psql gtfsdb
```

which loads the GTFS feed into the database `gtfsdb`. The database must already exist.


## Requirements

This scripts requires Python 3.
