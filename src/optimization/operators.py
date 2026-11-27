def clamp(chromosome , bounds):
    if len(chromosome) != len(bounds):
        raise ValueError("Chromosome and bounds must have the same lenghth")
    result = []
    for gene ,(low , high) in zip (chromosome , bounds):
        if low > high :
            raise ValueError("Invalid bounds")
        
        gene = int(gene)
        if gene < low :
            gene = low 
        elif gene > high :
            gene = high 
        result.append(gene)
        
    return result 
            


def crossover(parent1 , parent2 , crossover_rate ,rng):
    if len(parent1) != len(parent2):
        raise ValueError("Parents must have the same length")
    if rng.random() >= crossover_rate or len(parent1) < 2:
        return list(parent1), list(parent2)
    
    point = rng.randint(1, len(parent1) -1)
    
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
     
    return child1 , child2 


def mutate(chromosome , bounds , mutation_rate , rng):
    if len(chromosome) != len(bounds):
        raise ValueError("Chromosome and bounds must have the same length")
    
    mutated = list(chromosome)
    
    for i ,(low , high) in enumerate(bounds):
        if low > high :
            raise ValueError("Invalid bounds")
        
        if rng.random() < mutation_rate :
            mutated[i] = rng.randint(low , high)
            
    return mutated
    