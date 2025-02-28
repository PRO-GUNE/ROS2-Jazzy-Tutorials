import numpy as np
from typing import Callable, List, Union
import inspect


class LabTester:
    """
    A test helper class for validating 2D/3D rotation and transformation implementations
    """

    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0

    def assert_array_almost_equal(
        self,
        actual: np.ndarray,
        expected: np.ndarray,
        decimal: int = 6,
        message: str = "",
    ):
        """Custom assertion for numpy arrays with detailed output"""
        self.total_tests += 1
        try:
            np.testing.assert_array_almost_equal(actual, expected, decimal=decimal)
            print(f"✅ {message}")
            self.passed_tests += 1
        except AssertionError as e:
            print(f"❌ {message}")
            print(f"   Expected: {expected}")
            print(f"   Got: {actual}")

    def test_homogeneous_transform_2d(self, homogenous_transform_2D: Callable):
        """Test suite for 2D homogeneous transformation implementation"""
        print("\n=== Testing 2D Homogeneous Transformation Implementation ===")

        # Test 1: Given example - translation(3,4) + rotation(45°)
        point = np.array([1, 0])
        translation = np.array([3, 4])
        transformed = homogenous_transform_2D(point, translation, 45)
        self.assert_array_almost_equal(
            transformed,
            [3.707, 4.707],
            decimal=3,
            message="Combined transform: translation(3,4) + rotation(45°)",
        )

        # Test 2: Pure translation
        point = np.array([1, 2])
        translation = np.array([3, 4])
        transformed = homogenous_transform_2D(point, translation, 0)
        self.assert_array_almost_equal(
            transformed, [4, 6], message="Pure translation: no rotation"
        )

        # Test 3: Pure rotation
        point = np.array([1, 1])
        translation = np.array([0, 0])
        transformed = homogenous_transform_2D(point, translation, 30)
        self.assert_array_almost_equal(
            transformed,
            [0.366, 1.366],
            decimal=3,
            message="Pure rotation: no translation",
        )

        # Test 4: Rotate and translate
        point = np.array([1, 1])
        translation = np.array([4, 3])
        transformed = homogenous_transform_2D(point, translation, 90)
        self.assert_array_almost_equal(
            transformed, [3, 4], decimal=0, message="Translation and rotation"
        )

        # Test 3: Pure rotation
        point = np.array([1, 0])
        translation = np.array([0, 0])
        transformed = homogenous_transform_2D(point, translation, 90)
        self.assert_array_almost_equal(
            transformed, [0, 1], message="Pure rotation: no translation"
        )

        # Test 4: Combined rotation and translation
        point = np.array([1, 0])
        translation = np.array([2.25, 3.75])
        transformed = homogenous_transform_2D(point, translation, 90)
        self.assert_array_almost_equal(
            transformed,
            [2.250, 4.750],
            decimal=3,
            message="Combined rotation and translation",
        )

        # Test 5: Combined rotation and translation
        point = np.array([4, 3])
        translation = np.array([2, 3])
        transformed = homogenous_transform_2D(point, translation, 45)
        self.assert_array_almost_equal(
            transformed,
            [2.7071, 7.9498],
            decimal=3,
            message="Combined rotation and translation",
        )

        # Test 6: Combined rotation and translation far from origin
        point = np.array([10, 15])
        translation = np.array([100, 150])
        transformed = homogenous_transform_2D(point, translation, 60)
        self.assert_array_almost_equal(
            transformed,
            [92.00962, 166.16025],
            decimal=3,
            message="Combined rotation and translation",
        )

        # Test 7: Large rotations
        point = np.array([4, 3])
        translation = np.array([1, 1])
        transformed = homogenous_transform_2D(point, translation, 190)
        self.assert_array_almost_equal(
            transformed, [-2.41828648, -2.64901597],decimal=3,
            message="Large rotaions"
        )

        # Test 8
        point = np.array([2, 4])
        translation = np.array([-2, -1])
        transformed = homogenous_transform_2D(point, translation, 75)
        self.assert_array_almost_equal(
            transformed, [-5.34606521, 1.96712783],decimal=3,
            message="Combined transformation"
        )

        # Test 9
        point = np.array([-2, 2])
        translation = np.array([2, -2])
        transformed = homogenous_transform_2D(point, translation, 90)
        self.assert_array_almost_equal(
            transformed, [0, -4],decimal=3,
            message="Combined transformation"
        )

    def test_homogeneous_transform_3d(self, homogenous_transform_3D: Callable):
        """
        Test suite for 3D homogeneous transformation implementation

        Parameters:
        homogenous_transform_3D: function that takes (point: np.ndarray, translation: np.ndarray,
                           rotation_angles: dict) and returns transformed point
        """
        print("\n=== Testing 3D Homogeneous Transformation Implementation ===")

        # Test 1: Given example - translation(5,5,5) + rotation(90° about z-axis)
        point = np.array([2, 3, 4])
        translation = np.array([5, 5, 5])
        rotation = {"z": 90}  # rotation about z-axis
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [2, 7, 9],
            decimal=3,
            message="Combined 3D transform: translation(5,5,5) + rotation(90° about z)",
        )

        # Test 2: Pure translation in 3D
        point = np.array([1, 2, 3])
        translation = np.array([4, 5, 6])
        rotation = {"x": 0, "y": 0, "z": 0}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed, [5, 7, 9], message="Pure 3D translation: no rotation"
        )

        # Test 3: Pure rotation about x-axis
        point = np.array([1, 1, 0])
        translation = np.array([0, 0, 0])
        rotation = {"x": 90}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed, [1, 0, 1], decimal=3, message="Pure rotation about x-axis"
        )

        # Test 4: Combined rotations
        point = np.array([1, 0, 0])
        translation = np.array([0, 0, 0])
        rotation = {"x": 90, "y": 90, "z": 90}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [0, 0, 1],
            decimal=3,
            message="Combined rotations about x, y, and z axes",
        )

        # Test 5: Combined rotations
        point = np.array([1, 2, 3])
        translation = np.array([-1, -1, -1])
        rotation = {"x": 90, "y": 90, "z": 90}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [2, -3, 0],
            decimal=3,
            message="Rotations with Negative Translation",
        )

        # Test 6: Combined rotations
        point = np.array([1, 2, 3])
        translation = np.array([-5, 5, -1])
        rotation = {"x": 60, "y": 90, "z": 30}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [-2, 6, 1],
            decimal=3,
            message="Rotations by odd angles with Translation",
        )

        # Test 7: Combined rotations
        point = np.array([1, 2, 3])
        translation = np.array([0, 0, 0])
        rotation = {"x": 45, "y": 30, "z": 60}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [0.43301, -0.95323, 3.59219],
            decimal=3,
            message="Combined rotations about x, y, and z axes",
        )

        # Test 8: Combined rotations
        point = np.array([1, 2, 3])
        translation = np.array([1, 1, 1])
        rotation = {"x": 45, "y": 60, "z": 30}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [3.53109, 1.4356, 3.721],
            decimal=3,
            message="Combined rotations about x, y, and z axes with translation",
        )

        # Test 9: Combined rotations far from origin
        point = np.array([10, 15, 20])
        translation = np.array([100, 150, 200])
        rotation = {"x": 45, "y": 60, "z": 30}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [117.90064, 156.36056, 219.08168],
            decimal=3,
            message="Combined rotations about x, y, and z axes with translation",
        )

        # Test 10: Pure rotations of big angles
        point = np.array([1, 0, 1])
        translation = np.array([0, 0, 0])
        rotation = {"x": 120, "y": 150, "z": 250}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [0.7962, 1.07175, -0.46629],
            decimal=3,
            message="Pure rotations of big angles",
        )

        # Test 11: Combined rotations about negative angles with translation
        point = np.array([1, 0, 0])
        translation = np.array([1, 1, 1])
        rotation = {"x": -45, "y": -60, "z": -30}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed,
            [1.43301, 1.17678, 1.88388],
            decimal=3,
            message="Combined rotations about negative x, y, and z axes with translation",
        )

        # Test 12: Identity transformation
        point = np.array([2, 2, 3])
        translation = np.array([0, 0, 0])
        rotation = {'x': 0, 'y': 0, 'z': 0}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed, [2, 2, 3], decimal=3,
            message="Identity transformation"
        )

        # Test 13: Large rotations
        point = np.array([2, 1, 3])
        translation = np.array([1, 0, 2])
        rotation = {'x':360, 'y': 120, 'z': 240}
        transformed = homogenous_transform_3D(point, translation, rotation)
        self.assert_array_almost_equal(
            transformed, [3.66506351, -2.23205081, 0.6160254], decimal=3,
            message="Large rotations"
        )

    def test_chain_transformations(self, chain_transforms: Callable):
        """
        Test suite for chained transformation implementation

        Parameters:
        chain_transforms: function that takes (point: np.ndarray, transformations: List[dict])
                        where each dict contains 'translation' and 'rotation' keys
        """
        print("\n=== Testing Chain Transformations Implementation ===")

        # Test 1: Simple chain - two translations
        point = np.array([1, 1, 1])
        transforms = [
            {"translation": np.array([1, 0, 0]), "rotation": {"z": 0}},
            {"translation": np.array([0, 1, 0]), "rotation": {"z": 0}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed, [2, 2, 1], message="Chain of two translations"
        )

        # Test 2: Translation followed by rotation
        point = np.array([1, 0, 0])
        transforms = [
            {"translation": np.array([1, 0, 0]), "rotation": {"z": 0}},
            {"translation": np.array([0, 0, 0]), "rotation": {"z": 90}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [0, 2, 0],
            decimal=3,
            message="Translation followed by rotation",
        )

        # Test 3: Complex chain
        point = np.array([1, 0, 0])
        transforms = [
            {"translation": np.array([1, 1, 1]), "rotation": {"x": 90}},
            {"translation": np.array([0, 0, 1]), "rotation": {"y": 90}},
            {"translation": np.array([1, 0, 0]), "rotation": {"z": 90}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [0, 1, -1],
            decimal=3,
            message="Complex chain of transformations",
        )

        # Test 4: Identity chain
        point = np.array([1, 2, 3])
        transforms = [
            {"translation": np.array([0, 0, 0]), "rotation": {"x": 0}},
            {"translation": np.array([0, 0, 0]), "rotation": {"y": 0}},
            {"translation": np.array([0, 0, 0]), "rotation": {"z": 0}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed, point, message="Chain of identity transformations"
        )

        # Test 5: Complex chains
        point = np.array([1, 2, 3])
        transforms = [
            {
                "translation": np.array([1, 0, -1]),
                "rotation": {"x": 45, "y": 30, "z": 60},
            },
            {
                "translation": np.array([-1, 1, 0]),
                "rotation": {"x": 135, "y": 120, "z": 30},
            },
            {
                "translation": np.array([0, -1, 1]),
                "rotation": {"x": -90, "y": 60, "z": 0},
            },
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [1.8308927, -0.38874408, -2.0454028],
            decimal=3,
            message="Complex transformations",
        )

        # Test 6:
        point = np.array([1, 1, 1])
        transforms = [
            {
                "translation": np.array([1, 1, 1]),
                "rotation": {"x": 45, "y": 45, "z": 45},
            },
            {
                "translation": np.array([-1, -1, -1]),
                "rotation": {"x": -45, "y": -45, "z": -45},
            },
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [-1.16421356, 1.28033009, 1.48743687],
            decimal=4,
            message="Tranform * Reverse transform",
        )

        # Test 6: Complex chains
        point = np.array([1, 2, 3])
        transforms = [
            {
                "translation": np.array([1, 0, -1]),
                "rotation": {"x": 45, "y": 30, "z": 60},
            },
            {
                "translation": np.array([-1, 1, 0]),
                "rotation": {"x": 135, "y": 120, "z": 30},
            },
            {
                "translation": np.array([0, -1, 1]),
                "rotation": {"x": -90, "y": 60, "z": 0},
            },
            {
                "translation": np.array([1, 1, 1]),
                "rotation": {"x": 90, "y": 90, "z": 90},
            },
            {
                "translation": np.array([1, 1, 0]),
                "rotation": {"x": 135, "y": 120, "z": 30},
            },
            {
                "translation": np.array([0, 1, -1]),
                "rotation": {"x": -90, "y": 60, "z": 0},
            },
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [2.56055, -2.43085, -1.54043],
            decimal=3,
            message="Complex transformations with additional transform",
        )

        # Test 7: Complex chains
        point = np.array([4, 5, 6])
        transforms = [
            {
                "translation": np.array([1, 0, -1]),
                "rotation": {"x": 150, "y": 130, "z": 220},
            },
            {
                "translation": np.array([-1, 1, 0]),
                "rotation": {"x": 135, "y": 120, "z": 90},
            },
            {
                "translation": np.array([0, -1, 1]),
                "rotation": {"x": 120, "y": 270, "z": 110},
            },
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed,
            [0.99092, -9.01667, 1.72435],
            decimal=3,
            message="Complex transformations with big angles",
        )

        # Test 8: Complex chains
        point = np.array([3, 6, 9])
        transforms = [
            {
                "translation": np.array([1, 0, -1]),
                "rotation": {"x": -45, "y": 30, "z": -60},
            },
            {
                "translation": np.array([-1, 1, 0]),
                "rotation": {"x": -60, "y": -30, "z": -90},
            },
            {
                "translation": np.array([0, -1, 1]),
                "rotation": {"x": -45, "y": 30, "z": -30},
            },
            {
                "translation": np.array([1, 1, 1]),
                "rotation": {"x": 45, "y": -60, "z": -45},
            },
            {
                "translation": np.array([1, 1, 0]),
                "rotation": {"x": -30, "y": 60, "z": 30},
            },
            {
                "translation": np.array([0, 1, -1]),
                "rotation": {"x": -45, "y": 30, "z": -30},
            },
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(

            transformed, [8.04135, -2.03015, 7.18498], decimal=3,
            message="Complex transformations with nagative angles and additional transform"

        )

        # Test 9: Chains of Rotations Only
        point = np.array([3, 2, 4])
        transforms = [
            {'translation': np.array([0, 0, 0]), 'rotation': {'x': 0, 'y': 45, 'z': 45}},
            {'translation': np.array([0, 0, 0]), 'rotation': {'x': 45, 'y': 45, 'z': 0}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed, [4, 3, 2], 
            message="Chain of rotations"
        )
        
        # Test 10: Opposite transformations
        point = np.array([1, 1, 1])
        transforms = [
            {'translation': np.array([2, 2, 2]), 'rotation': {'x': 90, 'y': 90, 'z': 90}},
            {'translation': np.array([-2, -2, -2]), 'rotation': {'x': -90, 'y': -90, 'z': -90}},
        ]
        transformed = chain_transforms(point, transforms)
        self.assert_array_almost_equal(
            transformed, [-5, -1, 1],
            message="Opposite transformations"
        )


    def print_summary(self):
        """Print summary of test results"""
        print(f"\n=== Test Summary ===")
        print(f"Passed: {self.passed_tests}/{self.total_tests} tests")
        if self.passed_tests == self.total_tests:
            print("🎉 All tests passed!")
        else:
            print(f"❌ {self.total_tests - self.passed_tests} tests failed")
