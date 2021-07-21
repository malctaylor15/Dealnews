import os
import sys
import shutil
import datetime
import boto3
import zipfile
import logging 


def get_orderbook_dates_to_save(latest_day_dt, num_days):
    
    latest_day_dt = datetime.datetime.strptime(latest_day_dt, '%Y-%m-%d')
    # Determine which days to get folders for 
    start_date = latest_day_dt - datetime.timedelta(days = num_days)

    # Ensure start date is before end date and less than 10 days after 
    days_diff = (latest_day_dt - start_date).days
    assert(0 < days_diff < 10), f"""Difference between start and end dates is {days_diff} days 
            which is not between 0 and 10"""

    # Get the dates as a string between the window
    days_to_get = []
    while start_date < latest_day_dt:
        days_to_get.append(str(start_date.date()))
        start_date = start_date + datetime.timedelta(days=1)
    return(days_to_get)


def get_filename_filepath(days_to_get):
    base_path = '/mnt/volume-nyc3-01/Dealnews_Images/'

    paths_to_get = [base_path + x for x in days_to_get 
                    if os.path.isdir(base_path + x)]
    if len(paths_to_get) == 0:
        print("No paths to get... quitting")
        sys.exit("No folders available to zip")
        
    # Create file name 
    actual_start_date = min(paths_to_get)[-10:]
    actual_end_date = max(paths_to_get)[-10:]
    file_name = f'Dealnews_Images_{actual_start_date}__{actual_end_date}.zip'
    file_path = base_path + file_name
    file_path
    
    os.chdir(base_path)
    paths_to_get = [base_path + x for x in days_to_get 
                    if os.path.isdir(base_path + x)]

    # Create file name 
    actual_start_date = min(paths_to_get)[-10:]
    actual_end_date = max(paths_to_get)[-10:]
    file_name = f'Dealnews_Images_{actual_start_date}__{actual_end_date}.zip'
    file_path = base_path + file_name
    
    return(paths_to_get, file_name, file_path)

# Create the zip file

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def create_zip(file_path, paths_to_get):
            
    zipf = zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED)
    for path in paths_to_get:
        zipdir(path, zipf)
        print(f"Finished: {path}")
    zipf.close()
    print(f'Created: {file_path}')



#Upload to s3 
# s3_file_path = 'raw_orderbook_backups/'+file_name
# bucket = 'crypto-analysis-storage'
def upload_to_s3(file_path, bucket , s3_file_path):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    response = s3_client.upload_file(file_path, bucket , s3_file_path)
    print(f'Response: {response}')
    print(f'Uploaded: {file_path} to {bucket} and {s3_file_path}')


def delete_files(bucket, s3_file_path, paths_to_get, file_path):
    # Delete existing 
    boto3.resource('s3').Object(bucket, s3_file_path).load()
    os.remove(file_path)
    print(f"Deleted: {file_path}")
    for file in paths_to_get:
        shutil.rmtree(file)
        print(f"Deleted: {file}")
        


# In[7]:


def execute(latest_day_dt = str((datetime.datetime.now() - datetime.timedelta(days=7)).date()), num_days=7):
    days_to_get = get_orderbook_dates_to_save(latest_day_dt, num_days)
    print("Days to get: ", days_to_get) 
    
    paths_to_get, file_name, file_path = get_filename_filepath(days_to_get)
    print(f"File name: {file_name}, File path: {file_path}")
    
    create_zip(file_path, paths_to_get)
    
    s3_file_path = 'Dealnews/Images/'+file_name
    bucket = 'do-mt-backups'
    upload_to_s3(file_path, bucket , s3_file_path)
    delete_files(bucket, s3_file_path, paths_to_get, file_path)

if __name__ == '__main__':
    execute()





