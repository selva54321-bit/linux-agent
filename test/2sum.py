def two_sum(nums, target):
    """
    Given an array of integers nums and an integer target, return indices 
    of the two numbers such that they add up to target.
    Assumes exactly one solution exists.
    """
    num_map = {} # Dictionary to store {number: index}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            # Found the pair
            return [num_map[complement], i]
        # Store the current number and its index
        num_map[num] = i

# Example Usage:
# nums = [2, 7, 11, 15]
# target = 9
# print(two_sum(nums, target)) # Expected output: [0, 1] (since nums[0] + nums[1] == 9)

# nums = [3, 2, 4]
# target = 6
# print(two_sum(nums, target)) # Expected output: [1, 2]
