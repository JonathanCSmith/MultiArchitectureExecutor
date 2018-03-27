txt = '''{
  "cluster_user": "",
  "cluster_key": "",
  "login_ip": "",
  "submission_wrapper": {
      "identify_features.sh": "/camp/project/proj-emschaefer/working/processing/repos/MultiArchitectureExecutor/providers/cluster/slurm/slurm_submit_64.sh",
      "cube.sh": "/camp/project/proj-emschaefer/working/processing/repos/MultiArchitectureExecutor/providers/cluster/slurm/slurm_submit_big.sh",
      "default": "/camp/project/proj-emschaefer/working/processing/repos/MultiArchitectureExecutor/providers/cluster/slurm/slurm_submit.sh"
  },
  "logging_cleanup": false
}'''

import json
dic = json.loads(txt)