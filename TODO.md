# Drone Tracking TODO List

### Todo

- [ ] Change flight path data from raw XLSX loading to loading from the database
- [X] Get API Keys from the OS Environment
- [X] Verification of foreign keys for tracks, positions, etc. in ORM structure
- [X] Implementation of velocity and altitude in add_track functionality
- [X] Fix visualization and graphing features in views/templates
- [ ] Look into visualizing expected flight paths
- [ ] Optimize Javascript inside the HTML/js files
  - [ ] Don't request the full dataset, timestamp requests and only get NEW data
    - [ ] use plotly.extendtraces and don't constantly query the API
    - [ ] Sessionize and query based on a time
  - [ ] Don't request one drone at a time, instead have a singular endpoint to get all drone data
- [ ] Basic CRUD for drones, flights, and expected fligh paths
- [ ] Flight Save / Playback feature