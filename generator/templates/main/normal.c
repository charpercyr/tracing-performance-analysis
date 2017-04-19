#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

#include "%s%funch%%"

struct call_funcs_args
{
    int niter;
};

void* call_funcs(void* _args)
{
    struct call_funcs_args* args = _args;

    for(int i = 0; i < args->niter; i++)
    {
        %s%callfuncs%%
    }
    return NULL;
}

int main()
{
    pthread_t threads[%d%nthreads%%];
    struct call_funcs_args args = {
        .niter = %d%niter%% / %d%nthreads%%
    };

    for(int i = 0; i < %d%nsteps%%; i++)
    {
        for(int j = 0; j < %d%nthreads%%; j++)
            pthread_create(threads + j, NULL, call_funcs, &args);

        for(int j = 0; j < %d%nthreads%%; j++)
            pthread_join(threads[j], NULL);
    }

    return 0;
}