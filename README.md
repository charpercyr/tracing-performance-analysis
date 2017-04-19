# tracing-performance-analysis
This tool is used to generate, compile and run benchmark code for some tracing tools for comparison purpose.

## How to use
The basic usage is this:

`python3 generator.py <tool> <command> <args...>`

It will generate files in the directory `<tool>.out/`

### Generate
`python3 generator.py <tool> generate [-s steps] [-i iter] [-c count] [-t thread] [--inactive]

Will generate the source code for a specific tool.

* steps: Number of steps to execute
* iter: Number of iteration per step
* count: Number of functions to generate
* thread: Number of threads to run
* inactive: Flag to specify that the tool will place tracepoints but not activate them. It will generate code in `<tool>-d.out/ instead.

### Compile
`python3 generator.py <tool> compile [-s steps] [-i iter] [-c count] [-t thread] [--inactive] [--cflags cflags] [--ldflags ldflags] [--libs libs]

Will first call generate with the common arguments and then compile the generated source.

* Common arguments are the same as generate.
* cflags: Additional CFLAGS to pass to gcc
* ldflags: Additional LDFLAGS to pass to gcc
* libs: Additional libraries to link at link time

### Run
`python3 generator.py <tool> run <preset> [--threads threads] [--inactive]

Runs a preset

* preset is the configuration to use
    * time : Calculates execution time of 2^24 iterations.
    * memory : Will use valgrind to calculate used memory
    * start-time : Will run one tracepoint and calculate total executable time.
    * all : Runs the 3 presets above
* threads : Number of threads to run
* inactive : Same as generate/compile

# Clean
`python3 generator.py <tool> clean`

Removes all files generated for a tool