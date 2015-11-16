OS DEPENDENCIES
---------------
These dependencies are used to create build, test, and run environments.
They are used to generate packer or docker configs that then generate the
environments.

The schema is available via github as well, and can be used to validate your
requirements. After installing your runtime dependencies (`python setup.py
run_deps`), you can manually validate your os_dependencies using `pykwalify
--data-file /path/to/your/os_dependencies.yml --schema-file
.../[site|dist]-packages/auto_build_env/schema/os_dependencies.schema.<version>.yml`

REQUIRED KEYS
=============
The follow keys are required in each mapping.  Where they list a variable, the
variable is from /etc/os-release of the target OS.  With docker, they are
references to the docker registry
* `os_name`: this should match the NAME variable
* `os_version_id`: this should match the VERSION\_ID variable
* `docker_image`: This should match the docker image name
* `docker_image_tag`: The docker image tag
* `dependency_command`: the command line command used to install the
  dependencies

OPTIONAL KEYS
=============
The following 
* `run_depedency_list`: A list of runtime dependencies
* `build_dependency_list`: A list of build dependencies
* `test_dependency_list`: A list of testing dependencies (will be concatonated
  with the run dependencies but NOT the build)


VERSIONING
----------
The schema is versioned according to the following rules:
* If a required key is added, removed, or changed in a breaking way, the schema major version bumps
* If a non-required key is added, removed, or changed, OR a required key is
  changed in a non-breaking way, the minor version bumps
