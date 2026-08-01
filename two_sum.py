def two_sum(nums, target):
    num_map = {}
    for index, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], index]
        num_map[num] = index
    return []

if __name__ == "__main__":
    # Test cases
    nums1 = [2, 7, 11, 15]
    target1 = 9
    print(f"Input: nums={nums1}, target={target1}, Output: {two_sum(nums1, target1)}") # Expected: [0, 1] or [1, 0]

    nums2 = [3, 2, 4]
    target2 = 6
    print(f"Input: nums={nums2}, target={target2}, Output: {two_sum(nums2, target2)}") # Expected: [1, 2] or [2, 1]

    nums3 = [3, 3]
    target3 = 6
    print(f"Input: nums={nums3}, target={target3}, Output: {two_sum(nums3, target3)}") # Expected: [0, 1]

    nums4 = [1, 2, 3, 4, 5]
    target4 = 10
    print(f"Input: nums={nums4}, target={target4}, Output: {two_sum(nums4, target4)}") # Expected: []
