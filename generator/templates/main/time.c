#include <time.h>
#include <stdio.h>
#include <pthread.h>
#include <stdint.h>

#include "%s%funch%%"

struct call_funcs_args
{
    int niter;
};

void* call_funcs(void* _args)
{
    struct call_funcs_args* args = _args;
    int niter = args->niter;

    struct timespec begin, end;

    clock_gettime(CLOCK_THREAD_CPUTIME_ID, &begin);
    for(int i = 0; i < niter; i++)
    {
        %s%callfuncs%%
    }
    clock_gettime(CLOCK_THREAD_CPUTIME_ID, &end);

    uint64_t ret = ((uint64_t)end.tv_sec - (uint64_t)begin.tv_sec) * 1e9 + ((uint64_t)end.tv_nsec - (uint64_t)begin.tv_nsec);

    return (void*)ret;
}

int main()
{
    pthread_t threads[%d%nthreads%%];
    struct call_funcs_args args = {
        .niter = %d%niter%% / %d%nthreads%%
    };
    FILE* f = fopen("%s%testid%%.csv", "w");

    if(!f)
    {
        fprintf(stderr, "Can't open file %s%testid%%.csv");
        return 1;
    }

    fprintf(f, "Step,Time,Iterations\n");

    for(int i = 0; i < %d%nsteps%%; i++)
    {
        float total_time = 0;

        for(int j = 0; j < %d%nthreads%%; j++)
            pthread_create(threads + j, NULL, call_funcs, &args);

        for(int j = 0; j < %d%nthreads%%; j++)
        {
            uint64_t ttime;
            pthread_join(threads[j], (void*)&ttime);
            printf("%d %llu\n", j, ttime);
            total_time += ttime;
        }

        fprintf(f, "%d,%f,%d\n", i, (float)total_time / 1e9, %d%niter%%);
    }

    fclose(f);

    return 0;
}