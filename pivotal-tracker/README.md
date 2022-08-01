
# Setup
## Setup Pivotal Tracker `API Token`

```
export TRACER_TOKEN=${YOUR_TRACKER_API_TOKEN}
```

## Run

### Download and process
```python
python3 main.py
```

### Process local file
```shell
python3 main.py -i /Users/david/snapshots_2405917_20220801190946.json
```

## Find result

The output files are located at your `$HOME` directory with the name pattern of `snapshots_${project_name}_${timestamp}.csv`