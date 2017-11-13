import re
from collections import defaultdict
import networkx as nx
import operator
import matplotlib.pyplot as plt

reviews = 0
user = raw_input('Enter the user_id:')
number_of_similar_users = input('Enter integer:')

##create a customer dictionory of dictionaries to store all types of data of customer and item that he has reviewed
customer_data = defaultdict(lambda: defaultdict(list))
customers =[]
category_array = []
count = 0
count1 = 0
#################################Reads file and Extracts thenecessadry information from it########################################
def read_file():
    groupp = r'group:\s*(\w+)'
    p_id = r'Id:\s*(\d+)'
    asin = r'ASIN:\s*(\d+)'
    cust_id = r'cutomer:\s*(\w+)'    
    cust_size = r'total:\s*(\d+)'
    rate = r'rating:\s*(\d+)'
    helpful = r'helpful:\s*(\d+)'
    cate =  r'categories:\s*(\d+)'
    revi = r'total:\s*(\d+)'
    total_reviews = 0
    count = 0
    count1 = 0
    with open("/home/saikiran/Downloads/amazon-metadata.txt") as f:
        for line in f:       
            if re.findall(p_id, line):###Get the ids
                id_no = re.findall(r'Id:([^(]*)', line)[0]
                index = int(id_no)
                count1 = count1 +1            
            else:
                id2 = re.search(p_id, line)
                if id2:                
                    id_no = id2 
                    index = int(id_no.group(1))           
            review = re.search(cust_size,line)            
            if review:#get the review number
                reviews = int(review.group(1))
                if reviews > 0:                    
                    total_reviews += reviews
            customer_id = re.search(cust_id,line)
            customer_rating = re.search(rate,line)
            customer_geninue = re.search(helpful,line)
            if customer_id:#get the customer id and update dictionary with item ID : customers, customer_id:item_ids_rated, customer_id: item rattings,customer_id:geninue 
                if not customer_id.group(1) in customer_data[int(id_no)]['customers']:                
                    customer_data[int(id_no)]['customers'].append(customer_id.group(1))                    
                if not id_no in customer_data[customer_id.group(1)]['item_ids']:
                    customers.append(customer_id.group(1))
                    customer_data[customer_id.group(1)]['item_ids'].append(int(id_no))
                    customer_data[customer_id.group(1)]['cus_ratings'].append(int(customer_rating.group(1)))
                    customer_data[customer_id.group(1)]['cus_geninue'].append(int(customer_geninue.group(1)))             
            
            asin_no = re.search(asin,line)
            no_reviews = re.search(revi,line)
            if no_reviews:
                if int(no_reviews.group(1)[0]) == 0:
                    count = count +1       
            
            group = re.search(groupp,line)
            category = re.search(cate,line)
            if asin_no: #update Item_id:ASIN number               
                if not asin_no.group(1) in customer_data[int(id_no)]['asin_no']:
                    customer_data[int(id_no)]['asin_no'].append(asin_no.group(1))                    
#Completed retreiving all types of info for item and customer ############################################################################          
read_file()
customer_vectors =[]
customer_features =[]
#count = 0
customers = set(customers)
customer_rated_multiple_samegroup = []
customers_different = []
category_array = set(category_array)
#############################Process data in the required structure#############################
def process_data():    
    for k in customers:#for removing redundant customers from a single item    
        if len(customer_data[k]['item_ids'])> 1:#customer rated more than one item 
            if len(set(customer_data[k]['item_ids'])) < 2:#That is the customer rated multiple times for the same item              
               
                customer_data[k]['item_ids']= set(customer_data[k]['item_ids'])
                customer_data[k]['cus_ratings']= max(customer_data[k]['cus_ratings'])
                customer_data[k]['cus_geninue']= max(customer_data[k]['cus_geninue'])
            
process_data() 
print 'completed processing'
nodes_dict1 = {}
customer_nodes = {}
weightss = []
###################################Compute Weights between two users linked #####################################################################
def compute_weight_nodes():
    for k in customers:
        item_ids_rated_by_user = customer_data[k]['item_ids']
        length_items_rated_by_user = len(item_ids_rated_by_user)
        for items in item_ids_rated_by_user:
            custum = customer_data[int(items)]['customers']
            for c in custum:#other customers who rated same item as that of k customer                
                if (c,k) in nodes_dict1:
                    pass
                else:
                    weight = 0
                    ite = customer_data[c]['item_ids']
                    length_items__rated_dependent_user = len(ite)
                    intersection_ = list(set(item_ids_rated_by_user).intersection(ite))
                    for j in intersection_:
                        ind1 = list(customer_data[c]['item_ids']).index(j)
                        if isinstance( customer_data[c]['cus_ratings'], int ):
                            customer_data[c]['cus_ratings'] = [customer_data[c]['cus_ratings']]
                        rating1 =list(customer_data[c]['cus_ratings'])[ind1] 
                        ind2 = list(customer_data[k]['item_ids']).index(j)  
                        if isinstance( customer_data[k]['cus_ratings'], int ):
                            customer_data[k]['cus_ratings'] = [customer_data[k]['cus_ratings']]
                        rating2 =list(customer_data[k]['cus_ratings'])[ind2] 
                        weight = weight + float(5-(abs(rating1-rating2)))/float(len(customer_data[int(j)]['customers']))    
                    weight_based_on_common_item_rated_users = weight/length_items_rated_by_user
                    weightss.append(weight_based_on_common_item_rated_users)                    
                    nodes_dict1[(k,c)] =  weight_based_on_common_item_rated_users
                    
                 
compute_weight_nodes()
print 'completed weights'
nodes_dict = {}
#########################Normalise weights##################################################################
def normalise_weights():
    for a,b in nodes_dict1.items():        
        nodes_dict[a] = float(b - min(weightss))/float( max(weightss)- min(weightss))         
    return nodes_dict
nodes_dict = normalise_weights()
#############################Graph Building ##################################################################  
countt = 0
def graph_build():
    print 'graph building'
    G = nx.Graph()    
    for (a,b), value in nodes_dict.items():
        G.add_edge(a, b, weight=value)        
    return G
G = graph_build()
count2 =0
print 'neighbours calculating'
############################################Get n number of similar user to the user using BFS##############################################
def n_neighbor(G, start,n):
    total = 0
    similarity= {}
    #  {distance : [list of nodes at that distance]}
    distance_nodes = {}
    # nodes at distance 1 from the currently visited ones
    next_nodes = G.neighbors(start)
    # set of all visited nodes
    visited=set()
    visited.add(start)
    #print visited    
    distance = 0  # until we finish all the  nodes
    while len(next_nodes) > 0 and n > total:
        total = total + len(next_nodes)               
        # this will be the next node
        shell_after_this = []
        parent = list(visited)[-1:][0]
        # update distance
        distance += 1
        distance_nodes[distance] = []        
        # update visited and distance_nodes
        for node in next_nodes:
            visited.add(node)
            distance_nodes[distance].append(node)          
            if distance == 1:
                if (parent, node) in nodes_dict:
                    similarity[node] = nodes_dict[(parent, node)]
                else:
                    similarity[node] = nodes_dict[(node,parent)]
            else:
                pass
    
        # compute next_nodes_after_this
        for node in next_nodes:
            nodes =[]
            neighbors = []
            count = 0            
            # add neighbors to next_nodes_after_this
            # if they have not been visited already
            for neighbor in G.neighbors(node):                        
                if neighbor not in visited:
                    x = len(list(set(G.neighbors(neighbor)).intersection(visited)))
                    if x> 1:#If more than one neighbours for a given node we take average of all the visited surrounding nodes weights(taking the flow of the node for the simialrity calculation )
                        similarity[neighbor] = 0
                        for j in list(set(G.neighbors(neighbor)).intersection(visited)):
                            if (neighbor,j) in nodes_dict:
                                similarity[neighbor] =similarity[neighbor] + similarity[j]* nodes_dict[(neighbor,j)]
                            else:
                                similarity[neighbor] =similarity[neighbor] + similarity[j]* nodes_dict[(j,neighbor)]
                                
                        similarity[neighbor] = similarity[neighbor]/float(x)
                    else:#IF only one neighbour visited for a given node                      
                        count = count + 1
                        nodes.append(node)
                        neighbors.append(neighbor)                
                        try:
                            similarity[neighbor] = similarity[node]* nodes_dict[(neighbor,node)]
                        except:
                            similarity[neighbor] = similarity[node]* nodes_dict[(node,neighbor)]
                    shell_after_this.append(neighbor)
                #nh = neighbors           
        
        # we repeat with the new_shell
        next_nodes = set(shell_after_this)     
    if n <= total:#get top n users for the given user using similarity
        sorted_x = sorted(similarity.items(), key=operator.itemgetter(1),reverse=True)[:n]
        print sorted_x
    else:
        print 'There are only maximum of'+ str(total) + 'similar users to this' + start       
    return distance_nodes
k = n_neighbor(G, user,int(number_of_similar_users))
#print k