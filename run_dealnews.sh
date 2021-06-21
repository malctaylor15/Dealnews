# export path1="$(dirname "$0")"
cd /home/malcolm/Dealnews
echo "current working directory: "$PWD
DATE=`date +%m-%d-%y`
FILENAME=Scrape_Dealnews_${DATE}.ipynb
LOCATION=run_notebooks/
FILEPATH=$LOCATION$FILENAME

echo $FILEPATH
source /home/malcolm/main/bin/activate
papermill Scrape_Dealnews.ipynb $FILEPATH 
# When in QA use QA database
#papermill notebooks/Parse\ Meh\ API.ipynb $FILEPATH -p db_location data/meh_scraper_qa.db

export papermill_exit_status=$?
if [ $papermill_exit_status -eq 0 ]
then
  echo "removing "$FILEPATH
  rm $FILEPATH
fi

deactivate
exit 0

# 27 */4 * * * bash /home/malcolm/Dealnews/run_dealnews.sh > /home/malcolm/Dealnews/Logs/scraper.log 2>&1