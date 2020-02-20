#!/usr/bin/env python

import io
import csv
import os
from os.path import join
import sys
from argparse import ArgumentParser


# Make the list of all tables with the field definitions
tables = {
    'agency': [
        ('agency_id', 'varchar', 'primary key'),
        ('agency_name', 'varchar'),
        ('agency_url', 'varchar'),
        ('agency_timezone', 'varchar'),
        ('agency_lang', 'varchar'),
        ('agency_phone', 'varchar'),
    ],
    'calendar': [
        ('service_id', 'varchar', 'primary key'),
        ('monday', 'integer'),
        ('tuesday', 'integer'),
        ('wednesday', 'integer'),
        ('thursday', 'integer'),
        ('friday', 'integer'),
        ('saturday', 'integer'),
        ('sunday', 'integer'),
        ('start_date', 'date'),
        ('end_date', 'date'),
    ],
    'calendar_dates': [
        ('service_id', 'varchar'),
        ('date', 'date'),
        ('exception_type', 'integer'),
    ],
    'feed_info': [
        ('feed_publisher_name', 'varchar', 'primary key'),
        ('feed_publisher_url', 'varchar'),
        ('feed_lang', 'varchar'),
        ('feed_start_date', 'date'),
        ('feed_end_date', 'date'),
        ('feed_version', 'date'),
    ],
    'routes': [
        ('route_id', 'varchar', 'primary key'),
        ('agency_id', 'varchar'),
        ('route_short_name', 'varchar'),
        ('route_long_name', 'varchar'),
        ('route_desc', 'varchar'),
        ('route_type', 'integer'),
    ],
    'stops': [
        ('stop_id', 'varchar', 'primary key'),
        ('stop_name', 'varchar'),
        ('stop_lat', 'decimal', '(18,14)'),
        ('stop_lon', 'decimal', '(18,14)'),
        ('location_type', 'varchar'),
        ('parent_station', 'varchar'),
        ('geom', 'geometry'),
    ],
    'stop_times': [
        ('trip_id', 'varchar'),
        ('arrival_time', 'varchar'),
        ('departure_time', 'varchar'),
        ('stop_id', 'varchar'),
        ('stop_sequence', 'integer'),
        ('pickup_type', 'integer'),
        ('drop_off_type', 'integer'),
    ],
    'transfers': [
        ('from_stop_id', 'varchar'),
        ('to_stop_id', 'varchar'),
        ('transfer_type', 'integer'),
        ('min_transfer_time', 'integer'),
    ],
    'trips': [
        ('route_id', 'varchar'),
        ('service_id', 'varchar'),
        ('trip_id', 'varchar', 'primary key'),
        ('trip_headsign', 'varchar'),
        ('trip_short_name', 'varchar'),
        ('direction_id', 'integer'),
    ]
}



def create_schema(tables, schema, tbl_prefix):
    for tbl in tables.keys():
        sql = 'CREATE TABLE "%s"."%s%s" (\n' % (schema, tbl_prefix, tbl)
        fld_defs = []
        for fld in tables[tbl]:
            fld_defs.append('    "%s" ' % fld[0] + ' '.join(fld[1:]))
        sql += ',\n'.join(fld_defs) + '\n'
        sql += ');\n'
        print(sql)


def import_table(table, fields, schema, tbl_prefix, path):
    with io.open(path, encoding='utf-8-sig') as csvfile: 
        reader = csv.DictReader(csvfile) 
        for row in reader: 
            import_row(row, table, fields, schema, tbl_prefix)


def import_row(row, table, fields, schema, tbl_prefix):
    flds, vals = [], []
    for fld in fields:
        flds.append(fld[0])
        if fld[0] == 'geom':
            v = 'ST_SetSrid(ST_Point(%s, %s), 4326)' % (row['stop_lon'], row['stop_lat'])
        else:
            v = row.get(fld[0], None)
        vals.append(format_val(fld[1], v))
    print('INSERT INTO "%s"."%s%s" ("%s") VALUES (%s);' % (
        schema, tbl_prefix, table, 
        '", "'.join(flds), ', '.join(vals)
    ))


def format_val(frmt, val):
    if val is None:
        return 'NULL'
    if frmt in ('integer', 'decimal', 'geometry'):
        return val
    if frmt == 'date':
        return "'%s-%s-%s'" % (val[0:4], val[4:6], val[6:8])
    if frmt == 'varchar':
        return "'%s'" % val.replace("'", "''")



if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-s', '--schema', type=str, default='public',
        help="name of destination schema")
    ap.add_argument('-p', '--prefix', type=str, default='',
        help='prefix for the table names')
    ap.add_argument('gtfs', type=str,
        help='path to the GTFS directory')
    args = ap.parse_args()

    print('CREATE EXTENSION IF NOT EXISTS postgis;\n')
    if args.schema != 'public':
        print('CREATE SCHEMA IF NOT EXISTS "%s";\n' % args.schema)
    create_schema(tables, args.schema, args.prefix)
    for tbl, flds in tables.items():
        import_table(tbl, flds, args.schema, args.prefix, join(args.gtfs, tbl+'.txt'))
