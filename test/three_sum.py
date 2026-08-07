def threeSum(nums):
    """
    Finds all unique triplets in the array which sum up to zero.
    Args:
        nums (list[int]): The input list of integers.
    Returns:
        list[list[int]]: A list of unique triplets [a, b, c] such that a + b + c = 0.
    """
    # Sort the array to easily skip duplicates and use two pointers
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicate elements for 'a'
        if i > 0 and nums[i] == nums[i-1]:
            continue

        target = -nums[i]
        left, right = i + 1, n - 1

        while left <= right:
            current_sum = nums[left] + nums[right]
            if current_sum == target:
                # Found a triplet
                triplet = [nums[i], nums[left], nums[right]]
                result.append(triplet)
                
                # Move pointers and skip duplicates for 'b' and 'c'
                left += 1
                right -= 1
                while left <= right and nums[left] == nums[left - 1]:
                    left += 1
                while left <= right and nums[right] == nums[right + 1]:
                    right -= 1
            elif current_sum < target:
                # Need a larger sum, move left pointer up
                left += 1
            else:
                # Need a smaller sum, move right pointer down
                right -= 1

    return result

if __name__ == '__main__':
    # Example Test Case 1: Standard case
    nums1 = [-1, 0, 1, 2, -1, -4]
    print(f"Input: {nums1}")
    result1 = threeSum(nums1)
    print(f"Output: {result1}\n") # Expected: [[-1, -1, 2], [-1, 0, 1]]

    # Example Test Case 2: No solution case
    nums2 = [0, 1, 2]
    print(f"Input: {nums2}")
    result2 = threeSum(nums2)
    print(f"Output: {result2}\n") # Expected: []
