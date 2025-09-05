#include <stdio.h>
#include <microtime.h>
#include <string.h>
#include <stdlib.h>


typedef float* Matrix;


Matrix CreateMatrix(int Rows, int Cols)
{
  Matrix M;
  
  M = (Matrix) malloc(Rows*Cols*sizeof(M[0]));
  if(M==0)
    fprintf(stderr, "Matrix allocation failed in file %s, line %d\n", __FILE__, __LINE__);

  
  return M;
}
  


void FreeMatrix(Matrix M)
{

  if(M)
    free(M);
}



void InitMatrix(Matrix A, int Rows, int Cols)
{
  int i, j;

  for(i=0; i<Rows; i++)
    for(j=0; j<Cols; j++)
      A[i*Cols+j] = 1.0/(i+j+2);
}


void MatVecMult(Matrix A, Matrix B, Matrix C, int ARows, int ACols)
{
  int i, k;

  memset(C, 0, ARows*sizeof(C[0]));

  for(k=0; k<ACols; k++)
    for(i=0; i<ARows; i++)
      C[i] += A[i*ACols+k]*B[k];

}



int main(int argc, char **argv)
{
  
  int N, M, P=1;
  Matrix A, B, C;
  double t, time1, time2;

  if(argc != 2)
  {
    fprintf(stderr, "USAGE: %s Matrix-Dimension\n", argv[0]);
    exit(1);
  }
  
  N = atoi(argv[1]);
  M = N;

  A = CreateMatrix(N, M);
  B = CreateMatrix(M, P);
  C = CreateMatrix(N, P);


  InitMatrix(A, N, M);
  InitMatrix(B, M, P);  
  memset(C, 0, N*P*sizeof(C[0]));
  
  
  time1 = microtime();
  MatVecMult(A, B, C, N, M);
  time2 = microtime();
  
  t = time2-time1;
  printf("\nTime = %g us\tTimer Resolution = %g us\tPerformance = %g Gflop/s\n", t, get_microtime_resolution(), 2.0*N*N*1e-3/t);
  printf("C[N/2] = %g\n\n", (double) C[N/2]);

  FreeMatrix(A);
  FreeMatrix(B);
  FreeMatrix(C);


  return 0;
}
