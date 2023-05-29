# Parameters: 
# $1: yaml_file_name
# $2: resource-group
# $3: workspace-name

echo "1: $1"
echo "2: $2"
echo "3: $3"

if [ -n "$1" ] && [ -n "$2" ] && [ -n "$3" ]
  then
    job_id=$(az ml job create --file $1 --resource-group $2 --workspace-name $3 --query name -o tsv)
    echo "job_id: $job_id"
fi

# if [ -n "$job_id" ]
#   then
#     job_uri=$(az ml job show -n $job_id --resource-group $2 --workspace-name $3 --query services.Studio.endpoint)

#     echo $job_uri

#     running=("Queued" "NotStarted" "Starting" "Preparing" "Running" "Finalizing")
#     while [[ ${running[*]} =~ $status ]]
#     do
#       echo $job_uri
#       sleep 8 
#       status=$(az ml job show -n $job_id --resource-group $2 --workspace-name $3 --query status -o tsv)
#       echo $status
#     done

#     if [[ $status == "Completed" ]]
#     then
#       echo "Job completed"
#       exit 0
#     elif [[ $status == "Failed" ]]
#     then
#       echo "Job failed"
#       exit 1
#     else
#       echo "Job not completed or failed. Status is $status"
#       exit 2
#     fi

#     echo $job_uri
# else
#   echo "Job failed"
#   exit 1
# fi