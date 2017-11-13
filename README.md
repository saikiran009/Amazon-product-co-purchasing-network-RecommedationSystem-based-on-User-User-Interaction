# Amazon-product-co-purchasing-network-RecommedationSystem-based-on-User-User-Interaction


Problem Statement:
Given a query user one has to return the n similar users of that query user and give ranking based on similarity in a user-user network model.

Analyze the Data:
The data consists of information about Amazon Products which are of 4 types: Books, DVD’s, Music and Videos. Each product has its description and also consists of reviews given by the user.

Assumptions for the entire problem:
•	User has used the product only if he/she reviews the particular item. 
•	As of now the rating of the users is considered uniform: (biasness of the user ratings not considered) Ex: Say for some users (bad-ok-good){0-2,3,4-5} respectively for another user it may be (bad-ok-good){0,2,3}
•	The user- user is linked in a network only if there is at least a single common item that they have rated.(That is two users are directly related if they rate at least one common item)
Data Pre-Processing:
Extracted the related information using regular expressions. Extracted the entire useful data even the data that I haven’t used for this solution (Some scripts can be seen the meta_rough.py).
Created the dictionary of dictionaries for the customer data and item data consisting of different fields as keys and values as the corresponding information .
Building the Model:
We build the model such that two users have the direct relationship link if they have rated at least one common item (We can keep threshold as K items).
•	Building the Network:
The edge is built between users if they have rated at least one common item. The weight between the user-user is given by summation of decreasing_function (rating1-rating2)/(number_of_users_rated_for_that_common_item i)/frequency of the items rated by the user. 
Decreasing function:  5- (rating1-rating2).
Approaches that I used to solve the problem:
•	Used BFS and tried to implement the importance of the flow for a node to calculate similarity. (This is mainly based on the logical approach based on the network/model baseline that I have built).
•	Used N- Random Walks to know the more similar items for that query based on the number of times the node is hit and the weights associated with the neighbors and chances that it goes back to the given query user node  given the random walk from a particular query  user.


 Model 1:
•	BFS Implementation:
•	I normalized the weights such that the weights lie between( 0-1).Because here we assume that similarity diminishes from a query node as layer increases as we multiply the weights among the different layers.
•	I selected the query node user i and search for the next layer and assign similarity between user I and user j in next layer with edge weights.
•	For the next layer user k we multiply the before similarity of user j with user k to calculate the similarity between user i and user k .
•	If there are more surrounding users from the above layer for node k the average of the weights is taken but ideally it should have extra weightage as many nodes are passing into it so we can attach a constant c based on the number of flow and the layer at which the node is present from the query user.(But we didn’t consider that c For BFS )
•	I maintained the dictionary to track the similarity and the similar users and this stops once the criteria is reached that is getting N similar users.

 Model 2:
•	Truncated N  Random Walks
•	I initialized with raw weights without normalizing and converting them into probabilities from a particular node i. As the sum of probabilities of visiting it’s surrounding nodes should be one. Built the transition probability matrix. 
•	Built the neighboring matrix for further computation of h(i,j).
•	Select the query node and select the neighboring node randomly with the help of probability (say we run 1000 random walks and user i has 3 surrounding users(j,k,l) with weights 0.3, .2, 0.5 then we can say approx. chances 300 times it reaches j , 200 times reaches k and 500 times reaches i.)
•	We generate N truncated random walks for a particular length L and update h(I,j) and commute time (i,j).
•	If the random walk hits a node many times, then it’s close to the start node. We update this metric h(i,j)=1+P(i,n1)*h(n1,j)+P(i,n2)*h(n2,j)  for a graph {i : n1,n2} {n1:j}{n2:j}
We do summation for the neighboring of j node.
•	
With the help of this we can know the similarity of the node for a particular query node and it’s ranking.
•	As Random walks can go to random node for running for a long time we keep a threshold length L so that it walks over in that region.
•	This helps not to search the entire graph for similar nodes of a given query.

Comparing and Advantages of the one model over other:
The Shortest distance model doesn’t consider the flow of the node and entirely depends on the distance metric. The time complexity is too high for 1-n shortest distance mapping.
The BFS searches just the below layer for every node and gives importance to the level (biased). As we go next level similarity decreases for the coming node.  This may do not provide a strange node as a better similar to the query node and always weights its neighbors more than other layers. Fails in the case if the similar users doesn’t rate at least one common item and don’t have common neighbors. These are the drawbacks of my approach. 
Random Walk can overcome the above mentioned draw backs and it considers also the weightage between nodes as probabilities. As we run for almost high number of random walks (say 5000). Then the score for each node is updated and more the score more the similarity with the query node. Here a random node can be assigned which is similar to the query node. Some times this may be not useful so we restrict the length of the Random walk so that it walks within the specified region.
