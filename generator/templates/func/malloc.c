void %s%funcname%%(int iter)
{
    int* ptr = malloc(sizeof(int));
    *ptr = %d%funcidx%% + iter;
    printf("%p -> %d\n", ptr, *ptr);
    free(ptr);
}