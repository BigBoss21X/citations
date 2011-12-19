
#include <math.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <omp.h>

int verbose = 0;
int maxthreads = 1;
int maxthreads_train = 4;

double sigmoid(double x);
double max(double x,double y);
#define MIN(x,y) ((x)<(y)?(x):(y))

inline double sigmoid(double x) {
    if(x<-200) x = -200;
    else if(x>200) x = 200;
    return 1.0/(1.0+exp(-x));
}

inline double max(double x,double y) {
    if(x>y) return x; else return y;
}

void forward(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
             int k,float data[k][n],float outputs[k][l]) {
    if(verbose) printf("forward %d:%d:%d (%d)\n",n,m,l,k);
#pragma omp parallel for num_threads (maxthreads)
    for(int row=0;row<k;row++) {
        float *x = data[row];
        float y[m];
        float *z = outputs[row];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j];
            y[i] = sigmoid(total);
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
        }
    }
}

int argmax(int k,float z[k]) {
    int mi = 0;
    float mv = z[0];
    for(int i=1;i<k;i++) {
        if(z[i]<mv) continue;
        mv = z[i];
        mi = i;
    }
    return mi;
}

void classify(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
             int k,float data[k][n],int classes[k]) {
    if(verbose) printf("classify %d:%d:%d (%d)\n",n,m,l,k);
#pragma omp parallel for num_threads (maxthreads)
    for(int row=0;row<k;row++) {
        float *x = data[row];
        float y[m];
        float z[l];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j];
            y[i] = sigmoid(total);
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
        }
        classes[row] = argmax(l,z);
    }
}

void backward(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
              int k,float data[k][n],int classes[k],float eta,int ntrain,
              int nsamples,int samples[nsamples]) {
    if(verbose) printf("backward %d:%d:%d (%d)\n",n,m,l,k);
    assert(eta>0.0);
    assert(eta<10.0);
#pragma omp parallel for num_threads (maxthreads)
    for(int trial=0;trial<ntrain;trial++) {
        int row;
        if(nsamples>0) row = samples[(unsigned)(19.73*k*sin(trial))%nsamples];
        else row = (unsigned)(19.73*k*sin(trial))%k;
        // forward pass
        float *x = data[row];
        float y[m],z[l],delta2[l],delta1[m];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j];
            y[i] = sigmoid(total);
            assert(!isnan(y[i]));
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
            assert(!isnan(z[i]));
        }
        // backward pass
        int cls = classes[row];
        for(int i=0;i<l;i++) {
            double total = (z[i]-(i==cls));
            delta2[i] =  total * z[i] * (1-z[i]);
        }
        for(int i=0;i<m;i++) {
            double total = 0.0;
            for(int j=0;j<l;j++)
                total += delta2[j] *  w2[j][i];
            delta1[i] = total * y[i] * (1-y[i]);
        }
        for(int i=0;i<l;i++) {
            for(int j=0;j<m;j++) {
                w2[i][j] -= eta*delta2[i]*y[j];
            }
        }
        for(int i=0;i<m;i++) {
            for(int j=0;j<n;j++) {
                w1[i][j] -= eta*delta1[i]*x[j];
            }
        }
    }
}

typedef signed char byte;
#define BSCALE 100.0

void forward_b(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
               int k,byte data[k][n],float outputs[k][l]) {
    if(verbose) printf("forward %d:%d:%d (%d)\n",n,m,l,k);
#pragma omp parallel for num_threads (maxthreads)
    for(int row=0;row<k;row++) {
        byte *x = data[row];
        float y[m];
        float *z = outputs[row];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j]/BSCALE;
            y[i] = sigmoid(total);
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
        }
    }
}

void classify_b(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
                int k,byte data[k][n],int classes[k]) {
    if(verbose) printf("classify %d:%d:%d (%d)\n",n,m,l,k);
#pragma omp parallel for num_threads (maxthreads)
    for(int row=0;row<k;row++) {
        byte *x = data[row];
        float y[m];
        float z[l];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j]/BSCALE;
            y[i] = sigmoid(total);
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
        }
        classes[row] = argmax(l,z);
    }
}

void backward_b(int n,int m,int l,float w1[m][n],float b1[m],float w2[l][m],float b2[l],
                int k,byte data[k][n],int classes[k],float eta,int ntrain,
                int nsamples,int samples[nsamples]) {
    if(verbose) printf("backward %d:%d:%d (%d)\n",n,m,l,k);
    assert(eta>0.0);
    assert(eta<10.0);
#pragma omp parallel for num_threads (maxthreads_train)
    for(int trial=0;trial<ntrain;trial++) {
        int row;
        if(nsamples>0) row = samples[(unsigned)(19.73*k*sin(trial))%nsamples];
        else row = (unsigned)(19.73*k*sin(trial))%k;
        // forward pass
        byte *x = data[row];
        float y[m],z[l],delta2[l],delta1[m];
        for(int i=0;i<m;i++) {
            double total = b1[i];
            for(int j=0;j<n;j++) total += w1[i][j]*x[j]/BSCALE;
            y[i] = sigmoid(total);
            assert(!isnan(y[i]));
        }
        for(int i=0;i<l;i++) {
            double total = b2[i];
            for(int j=0;j<m;j++) total += w2[i][j]*y[j];
            z[i] = sigmoid(total);
            assert(!isnan(z[i]));
        }
        // backward pass
        int cls = classes[row];
        for(int i=0;i<l;i++) {
            double total = (z[i]-(i==cls));
            delta2[i] =  total * z[i] * (1-z[i]);
        }
        for(int i=0;i<m;i++) {
            double total = 0.0;
            for(int j=0;j<l;j++)
                total += delta2[j] *  w2[j][i];
            delta1[i] = total * y[i] * (1-y[i]);
        }
        for(int i=0;i<l;i++) {
            for(int j=0;j<m;j++) {
                w2[i][j] -= eta*delta2[i]*y[j];
            }
        }
        for(int i=0;i<m;i++) {
            for(int j=0;j<n;j++) {
                w1[i][j] -= eta*delta1[i]*x[j]/BSCALE;
            }
        }
    }
}
