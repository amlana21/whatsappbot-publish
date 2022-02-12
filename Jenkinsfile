pipeline{

    agent any
    environment{
        AWS_ACCESS_KEY_ID=credentials('awsaccesskey')
        AWS_SECRET_ACCESS_KEY=credentials('awssecretkey')
        AWS_DEFAULT_REGION="us-east-1"
        SKIP="N"
        TERRADESTROY="Y"
        FIRST_DEPLOY="Y"
        STATE_BUCKET="whatsappbotstateac"
        REGISTRY_URL="<registry_url>"
    }


    stages{
        stage("Create Terraform State Buckets"){
            when{
                environment name:'FIRST_DEPLOY',value:'Y'
                environment name:'TERRADESTROY',value:'N'
            }
            steps{
                bat'''
                aws s3 mb s3://<bucket_name>'''
                
            }
        }

        stage("Deploy Kube cluster"){
            when{
                environment name:'FIRST_DEPLOY',value:'Y'
                environment name:'TERRADESTROY',value:'N'
                environment name:'SKIP',value:'Y'
            }
            stages{
                        stage('Validate infra'){
                            steps{
                                sh '''
                                cd api_infrastructure
                                terraform init
                                terraform validate'''
                            }
                        }
                        stage('Deploy cluster'){
                             
                            steps{
                                sh '''
                                cd api_infrastructure
                                terraform plan -out outfile
                                terraform apply outfile'''
                                sleep 20
                            }
                        }
                        stage('test kubectl'){
                            steps{
                                sh '''
                                cd api_infrastructure
                                aws eks update-kubeconfig --name <cluster_name> 
                                kubectl get nodes'''
                            }
                        }
                    }
        }

        stage("Build Docker images"){
            when{
                environment name:'FIRST_DEPLOY',value:'Y'
                environment name:'TERRADESTROY',value:'N'
                environment name:'SKIP',value:'Y'
            }
            stages{
                stage('Build callback api'){
                    steps{
                        sh '''
                        mkdir callbackapi
                        '''
                        dir('callbackapi') {
                            checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'githubaccess', url: '<callback_api_git_url>']]])
                        
                        }
                        sh 'docker login registry.gitlab.com -u $IMAGE_CREDS_USR -p $IMAGE_CREDS_PSW'
                        sh '''
                        cd callbackapi
                        docker build --no-cache -t $REGISTRY_URL/<image_name> .
                        docker push $REGISTRY_URL/<image_name>
                        ls -a
                        '''
                    }
                    
                }
                stage('Build backend api'){
                    steps{
                        sh '''
                        mkdir agentapi
                        '''
                        dir('agentapi') {
                            checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'githubaccess', url: '<backend_api_git_url>']]])
                        
                        }
                        sh 'docker login registry.gitlab.com -u $IMAGE_CREDS_USR -p $IMAGE_CREDS_PSW'
                        sh '''
                        cd agentapi
                        docker build --no-cache -t $REGISTRY_URL/<image_name> .
                        docker push $REGISTRY_URL/<image_name>
                        ls -a
                        '''
                    }
                    
                }
            }
            
        }


        stage("Deploy Kube"){
            when{
                environment name:'FIRST_DEPLOY',value:'Y'
                environment name:'TERRADESTROY',value:'N'
                environment name:'SKIP',value:'N'
            }
            stages{
                stage('get kube creds'){
                        steps{
                                sh 'aws eks update-kubeconfig --name <cluster_name>'
                            }
                        }
                stage('create secret'){
                    steps{
                        sh '''
                            cd kube_yamls
                            kubectl apply -f registrySecret.yml'''
                    }
                }
                stage('create config'){
                    steps{
                        sh '''
                        cd kube_yamls
                        kubectl apply -f configMaps.yml
                        '''
                    }
                }

                stage('deploy'){
                    parallel{
                stage('callback api'){
                    stages{
                        stage('get kube creds'){
                            steps{
                                sh 'aws eks update-kubeconfig --name <cluster_name>'
                            }
                        }
                        stage('deploy kube yaml'){
                            steps{
                                sh '''
                                cd kube_yamls
                                kubectl apply -f wsapp_callback_api.yml'''
                            }
                        }
                    }
                    
                    
                }
                stage('agent api'){
                    stages{
                        stage('get kube creds'){
                            steps{
                                sh 'aws eks update-kubeconfig --name <cluster_name>'
                            }
                        }
                        stage('deploy kube yaml'){
                            steps{
                                sh '''
                                cd kube_yamls
                                kubectl apply -f wsapp_agent_api.yml'''
                            }
                        }
                    }
                    
                    
                }
            }
                }

                


            }
            
        }



        stage("Deploy lex Lambda"){
            when{
                    environment name:'TERRADESTROY',value:'N'
                    environment name:'SKIP',value:'Y'
                }
             stages{
                        stage('Validate infra'){
                            steps{
                                sh '''
                                cd lexlambda
                                terraform init
                                terraform validate'''
                            }
                        }
                        stage('Deploy api lambda'){
                             when{
                                environment name:'FIRST_DEPLOY',value:'Y'
                                }
                            steps{
                                sh '''
                                cd lexlambda
                                terraform plan -out outfile
                                terraform apply outfile'''
                            }
                        }
                        stage('Update api lambda'){
                             when{
                                environment name:'FIRST_DEPLOY',value:'N'
                                }
                            steps{
                                sh '''
                                cd lexlambda
                                terraform apply -replace="module.stock-api-lambda.module.lambda_function_local.aws_lambda_function.this[0]" -replace="aws_s3_bucket_object.stock_api_lambda" -auto-approve'''
                            }
                        }
                    }

        }





        stage("Run Destroy"){
            when{
                environment name:'TERRADESTROY',value:'Y'
            }
            stages{
                stage("Destroy lex Lambda"){
                    when{
                        environment name:'SKIP',value:'Y'
                    }
                    steps{
                        sh '''
                            cd lexlambda
                            terraform destroy -auto-approve
                            '''
                    }
                }

                stage("Destroy eks cluster"){
                    steps{
                        sh '''
                            cd api_infrastructure
                            terraform init
                            terraform destroy -auto-approve
                            '''
                    }
                }

                //next stage

                stage("Destroy state bucket"){
                    steps{
                        sh '''
                            aws s3 rb s3://<bucket_name> --force
                            '''
                    }
                }
            }
        }

        

    }

    post { 
        always { 
            cleanWs()
        }
    }


}