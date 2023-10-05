#echo sudo docker build --tag bvb-shop .
sudo docker build --tag bvb-shop .
#echo sudo docker run bvb-shop -p 1111:1111 bvb-shop
sudo docker run -p 1111:1111 bvb-shop
