# Hotspot Analyser

This repo contains a simple tool used to analyse 'Hotspots' in a git repo for 
a given time period. It was developed for [one of the essays](https://desosa2020.netlify.com/projects/sentry/2020/03/23/monitoring-sentrys-software-quality.html)
we had to write for the IN4315 course at Delft University of Technology. In 
this essay we analysed the areas of [Sentry](https://github.com/getsentry/sentry) 
that were currently under development by looking at the folders that were 
touched by the most commits.

The Python script used is included in this repo.  It makes use of `git` which 
has to be installed and accessible from the place you run this script.

The script can be run with a given set of flags that were put in to make it 
easy to perform analyses over the repo for different time frames. To run the 
script one should place it inside the git repository you want to analyse and 
call:
```bash
# Analyse the commits between 2018-06-25T00:00:00 and 2020-01-07T00:00:00.
# In the case of Sentry this is the period between releasing v9 and v10.
python3 analyser.py \
  --after="2018-06-25T00:00:00" \
  --before="2020-01-07T00:00:00" \
  --out folder-hits-v9-v10.txt
```

The results are then written to file and look as follows:
```
MIN	AVG	MAX	FOLDER
1	52	202	src/sentry/conf/
3	21	39	src/sentry/search/snuba/
6	20	34	src/sentry/static/sentry/app/components/smartSearchBar/
3	17	55	src/sentry/integrations/vsts/
2	17	58	src/sentry/options/
3	16	41	src/sentry/tagstore/snuba/
16	16	16	src/sentry/static/sentry/app/views/releases/list/organizationReleases/
1	15	44	src/sentry/lang/native/
1	14	68	src/sentry/features/
2	13	40	src/sentry/static/sentry/app/views/organizationEvents/
...
```

It is shared here as it might prove useful to somebody else.
