def threeSum(nums):
    """
    Finds all unique triplets in the array which give the sum of zero.
    Time Complexity: O(n^2)
    Space Complexity: O(1) (excluding output storage)
    """
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicate elements for the first number of the triplet
        if i > 0 and nums[i] == nums[i-1]:
            continue

        left, right = i + 1, n - 1
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            if current_sum == 0:
                result.append(sorted([nums[i], nums[left], nums[right]]))
                # Move pointers and skip duplicates for the second and third numbers
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else: # current_sum > 0
                right -= 1

    return result

# Example Usage:
if __name__ == "__main__":
    nums1 = [-1, 0, 1, 2, -1, -4]
    print(f"Input: {nums1}")
    print("Output:", threeSum(nums1)) # Expected: [[-1, -1, 2], [-1, 0, 1]]

    nums2 = [0, 0, 0]
    print(f"\nInput: {nums2}")
    print("Output:", threeSum(nums2)) # Expected: [[0, 0, 0]]

    nums3 = [1, 2, 3]
    print(f"\nInput: {nums3}")
    print("Output:", threeSum(nums3)) # Expected: []