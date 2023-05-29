# Parameters: 
# $1: yaml_file_name
# $2: resource-group
# $3: workspace-name

echo "1: $1"
echo "2: $2"
echo "3: $3"

if [ -n "$1" ] && [ -n "$2" ] && [ -n "$3" ]
  then
    job_id=$(az ml component create --file $1 --resource-group $2 --workspace-name $3 --query name -o tsv)
    echo "job_id: $job_id"
fi
