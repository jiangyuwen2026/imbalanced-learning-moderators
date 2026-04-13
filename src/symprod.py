"""
SyMProD: Synthetically Minority Over-sampling with Probabilistic Distribution

Implementation based on:
    Tum, P., Tantisantiwong, N., & Tam, W. M. (2020). 
    Effective minority class generation for credit scoring using 
    synthetically minority oversampling with probabilistic distribution. 
    IEEE Access, 8, 129576-129585.

Core Algorithm:
    1. Compute closeness factor between minority and majority samples
    2. Assign probability based on closeness factor
    3. Generate synthetic samples using weighted interpolation
"""

import numpy as np
from typing import Optional, Tuple, List
from sklearn.neighbors import NearestNeighbors
import warnings


class SyMProD:
    """
    SyMProD Oversampling Algorithm
    
    Parameters
    ----------
    ct : float, default=1.0
        Closeness threshold. Controls the boundary between minority and majority regions.
        Higher CT means stricter minority region definition.
    k : int, default=5
        Number of nearest neighbors for synthetic sample generation.
    m : int, default=100
        Maximum number of synthetic samples to generate per minority instance.
    random_state : int, optional
        Random seed for reproducibility.
    
    Attributes
    ----------
    ct_ : float
        Fitted closeness threshold (same as ct parameter)
    n_samples_ : int
        Number of synthetic samples generated
    """
    
    def __init__(
        self,
        ct: float = 1.0,
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None
    ):
        self.ct = ct
        self.k = k
        self.m = m
        self.random_state = random_state
        
        # Attributes set during fit
        self.ct_ = ct
        self.n_samples_ = 0
        self._rng = np.random.RandomState(random_state)
        
    def _compute_closeness_factor(
        self,
        X_minority: np.ndarray,
        X_majority: np.ndarray
    ) -> np.ndarray:
        """
        Compute closeness factor for each minority sample.
        
        Closeness Factor (CF) measures how close a minority sample is to 
        the majority class boundary.
        
        CF = (Distance to k-th nearest majority) / (Mean distance to k nearest majority)
        
        Lower CF means the sample is closer to majority class (more dangerous).
        Higher CF means the sample is deeper in minority region (safer).
        
        Parameters
        ----------
        X_minority : array-like of shape (n_minority, n_features)
            Minority class samples
        X_majority : array-like of shape (n_majority, n_features)
            Majority class samples
            
        Returns
        -------
        cf : ndarray of shape (n_minority,)
            Closeness factor for each minority sample
        """
        n_minority = len(X_minority)
        
        # Fit k-NN on majority class
        nn_majority = NearestNeighbors(n_neighbors=self.k, metric='euclidean')
        nn_majority.fit(X_majority)
        
        # Find k nearest majority neighbors for each minority sample
        distances, _ = nn_majority.kneighbors(X_minority)
        
        # Compute closeness factor
        # CF = d_k / mean(d_1, d_2, ..., d_k)
        cf = np.zeros(n_minority)
        for i in range(n_minority):
            d_k = distances[i, -1]  # k-th nearest distance
            d_mean = np.mean(distances[i])  # mean of k nearest distances
            if d_mean > 0:
                cf[i] = d_k / d_mean
            else:
                cf[i] = 1.0  # Handle edge case
                
        return cf
    
    def _compute_sampling_probabilities(
        self,
        cf: np.ndarray
    ) -> np.ndarray:
        """
        Compute sampling probability based on closeness factor.
        
        Samples with CF < CT are in the "danger zone" and get higher probability.
        Samples with CF >= CT are in "safe zone" and may get lower or zero probability.
        
        Parameters
        ----------
        cf : ndarray of shape (n_minority,)
            Closeness factors
            
        Returns
        -------
        prob : ndarray of shape (n_minority,)
            Sampling probabilities (sum to 1)
        """
        # Mask for samples in danger zone (CF < CT)
        danger_mask = cf < self.ct_
        
        # Compute weights: inverse of CF for danger zone samples
        weights = np.zeros(len(cf))
        weights[danger_mask] = 1.0 / (cf[danger_mask] + 1e-10)
        
        # Normalize to probabilities
        if weights.sum() > 0:
            prob = weights / weights.sum()
        else:
            # Fallback: uniform distribution
            prob = np.ones(len(cf)) / len(cf)
            
        return prob
    
    def _generate_synthetic_sample(
        self,
        x_i: np.ndarray,
        X_minority: np.ndarray,
        nn_minority: NearestNeighbors
    ) -> np.ndarray:
        """
        Generate a single synthetic sample.
        
        Uses weighted interpolation between the seed minority sample
        and its k nearest minority neighbors.
        
        Parameters
        ----------
        x_i : ndarray of shape (n_features,)
            Seed minority sample
        X_minority : ndarray of shape (n_minority, n_features)
            All minority samples
        nn_minority : NearestNeighbors
            Fitted nearest neighbors on minority class
            
        Returns
        -------
        x_syn : ndarray of shape (n_features,)
            Synthetic sample
        """
        # Find k nearest minority neighbors (excluding self)
        distances, indices = nn_minority.kneighbors([x_i])
        
        # Exclude the sample itself (first neighbor with distance 0)
        valid_neighbors = indices[0][distances[0] > 1e-10]
        
        if len(valid_neighbors) == 0:
            # If no valid neighbors, return the sample itself with small noise
            return x_i + self._rng.normal(0, 0.01, size=x_i.shape)
        
        # Select a random neighbor (with probability inversely proportional to distance)
        neighbor_dists = distances[0][distances[0] > 1e-10]
        neighbor_weights = 1.0 / (neighbor_dists + 1e-10)
        neighbor_probs = neighbor_weights / neighbor_weights.sum()
        
        neighbor_idx = self._rng.choice(valid_neighbors, p=neighbor_probs)
        x_neighbor = X_minority[neighbor_idx]
        
        # Generate synthetic sample using interpolation
        # x_syn = x_i + alpha * (x_neighbor - x_i)
        # where alpha is random in [0, 1]
        alpha = self._rng.random()
        x_syn = x_i + alpha * (x_neighbor - x_i)
        
        return x_syn
    
    def fit_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit the model and resample the dataset.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data
        y : array-like of shape (n_samples,)
            Target labels (binary: 0 for majority, 1 for minority)
            
        Returns
        -------
        X_resampled : ndarray of shape (n_samples_new, n_features)
            Resampled features
        y_resampled : ndarray of shape (n_samples_new,)
            Resampled labels
        """
        X = np.asarray(X)
        y = np.asarray(y)
        
        # Separate majority and minority classes
        minority_class = 1
        majority_class = 0
        
        X_minority = X[y == minority_class]
        X_majority = X[y == majority_class]
        
        n_minority = len(X_minority)
        n_majority = len(X_majority)
        
        if n_minority == 0:
            raise ValueError("No minority samples found in the dataset")
        if n_majority == 0:
            raise ValueError("No majority samples found in the dataset")
        
        # Calculate how many synthetic samples to generate
        n_synthetic = n_majority - n_minority
        
        if n_synthetic <= 0:
            warnings.warn("Dataset is already balanced or minority is majority. "
                         "Returning original dataset.")
            return X.copy(), y.copy()
        
        # Step 1: Compute closeness factors
        cf = self._compute_closeness_factor(X_minority, X_majority)
        
        # Step 2: Compute sampling probabilities
        sampling_prob = self._compute_sampling_probabilities(cf)
        
        # Step 3: Generate synthetic samples
        # Fit k-NN on minority class for synthetic generation
        nn_minority = NearestNeighbors(n_neighbors=min(self.k + 1, n_minority), 
                                       metric='euclidean')
        nn_minority.fit(X_minority)
        
        synthetic_samples = []
        samples_per_instance = np.random.multinomial(
            n_synthetic, 
            sampling_prob
        )
        
        for i, n_gen in enumerate(samples_per_instance):
            n_gen = min(n_gen, self.m)  # Cap at maximum per instance
            for _ in range(n_gen):
                x_syn = self._generate_synthetic_sample(
                    X_minority[i], X_minority, nn_minority
                )
                synthetic_samples.append(x_syn)
        
        # Convert to array
        if len(synthetic_samples) > 0:
            X_synthetic = np.array(synthetic_samples)
            y_synthetic = np.full(len(synthetic_samples), minority_class)
            
            # Combine original and synthetic
            X_resampled = np.vstack([X, X_synthetic])
            y_resampled = np.hstack([y, y_synthetic])
        else:
            X_resampled = X.copy()
            y_resampled = y.copy()
        
        self.n_samples_ = len(synthetic_samples)
        
        return X_resampled, y_resampled
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'SyMProD':
        """Fit the model (no-op, for API compatibility)."""
        return self
    
    def resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Alias for fit_resample."""
        return self.fit_resample(X, y)


class SyMProD_ENN(SyMProD):
    """
    SyMProD with ENN (Edited Nearest Neighbors) cleaning.
    
    Based on Chen (2024) improvement:
    1. Remove outliers using Isolation Forest (optional pre-processing)
    2. Apply SyMProD oversampling
    3. Clean synthetic samples using ENN
    
    Parameters
    ----------
    ct : float, default=1.0
        Closeness threshold
    k : int, default=5
        Number of neighbors for synthetic generation
    m : int, default=100
        Max synthetic samples per instance
    enn_k : int, default=3
        Number of neighbors for ENN cleaning
    use_isolation_forest : bool, default=False
        Whether to remove outliers before oversampling
    contamination : float, default=0.1
        Expected proportion of outliers (for Isolation Forest)
    random_state : int, optional
        Random seed
    """
    
    def __init__(
        self,
        ct: float = 1.0,
        k: int = 5,
        m: int = 100,
        enn_k: int = 3,
        use_isolation_forest: bool = False,
        contamination: float = 0.1,
        random_state: Optional[int] = None
    ):
        super().__init__(ct=ct, k=k, m=m, random_state=random_state)
        self.enn_k = enn_k
        self.use_isolation_forest = use_isolation_forest
        self.contamination = contamination
    
    def _remove_outliers(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Remove outliers using Isolation Forest."""
        from sklearn.ensemble import IsolationForest
        
        iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state
        )
        
        # Fit on minority class only
        minority_mask = y == 1
        outlier_labels = iso_forest.fit_predict(X[minority_mask])
        
        # Keep inliers (label=1)
        inlier_mask = np.ones(len(y), dtype=bool)
        inlier_mask[minority_mask] = (outlier_labels == 1)
        
        return X[inlier_mask], y[inlier_mask]
    
    def _enn_cleaning(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Apply ENN cleaning to remove misclassified samples."""
        from sklearn.neighbors import KNeighborsClassifier
        
        knn = KNeighborsClassifier(n_neighbors=self.enn_k)
        knn.fit(X, y)
        
        # Predict on the same data
        y_pred = knn.predict(X)
        
        # Keep samples where prediction matches true label
        correct_mask = (y_pred == y)
        
        return X[correct_mask], y[correct_mask]
    
    def fit_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Fit and resample with optional outlier removal and ENN cleaning."""
        X_clean, y_clean = X.copy(), y.copy()
        
        # Step 1: Remove outliers (optional)
        if self.use_isolation_forest:
            X_clean, y_clean = self._remove_outliers(X_clean, y_clean)
        
        # Step 2: Apply SyMProD oversampling
        X_resampled, y_resampled = super().fit_resample(X_clean, y_clean)
        
        # Step 3: ENN cleaning
        X_cleaned, y_cleaned = self._enn_cleaning(X_resampled, y_resampled)
        
        return X_cleaned, y_cleaned
