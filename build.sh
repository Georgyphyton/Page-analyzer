#!/usr/bin/env bash

psql -a -d $DATABASE_URL -f database.sql