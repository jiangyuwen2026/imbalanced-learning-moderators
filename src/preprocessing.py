"""
Data Preprocessing Module for Credit Scoring

Includes:
    - Z-score standardization
    - Outlier removal using statistical thresholds
    - Label encoding
    - Train/validation/test splitting
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, Union, List, Dict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split


class DataPreprocessor:
    """
    Data preprocessor for credit scoring datasets.
    
    Parameters
    ----------
    z_score_threshold : float, default=3.0
        Z-score threshold for outlier removal (NT in methodology)
    remove_outliers : bool, default=True
        Whether to remove outliers
    scale_features : bool, default=True
        Whether to apply Z-score standardization
    random_state : int, optional
        Random seed for reproducibility
    
    Attributes
    ----------
    scaler_ : StandardScaler
        Fitted scaler
    n_outliers_removed_ : int
        Number of outliers removed
    feature_names_ : list
        Names of features after preprocessing
    """
    
    def __init__(
        self,
        z_score_threshold: float = 3.0,
        remove_outliers: bool = True,
        scale_features: bool = True,
        random_state: Optional[int] = None
    ):
        self.z_score_threshold = z_score_threshold
        self.remove_outliers = remove_outliers
        self.scale_features = scale_features
        self.random_state = random_state
        
        # Attributes set during fit
        self.scaler_ = None
        self.n_outliers_removed_ = 0
        self.feature_names_ = None
        self._label_encoder = None
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame], y=None) -> 'DataPreprocessor':
        """
        Fit the preprocessor.
        
        Parameters
        ----------
        X : array-like
            Feature matrix
        y : array-like, optional
            Target variable (not used, for API compatibility)
            
        Returns
        -------
        self : DataPreprocessor
        """
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
            X = X.values
        else:
            X = np.asarray(X)
            self.feature_names_ = [f"feature_{i}" for i in range(X.shape[1])]
        
        if self.scale_features:
            self.scaler_ = StandardScaler()
            self.scaler_.fit(X)
        
        return self
    
    def transform(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[Union[np.ndarray, pd.Series]] = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, Optional[np.ndarray]]]:
        """
        Transform the data.
        
        Parameters
        ----------
        X : array-like
            Feature matrix
        y : array-like, optional
            Target variable
            
        Returns
        -------
        X_transformed : ndarray
            Transformed features
        y_transformed : ndarray, optional
            Transformed target (if y provided)
        """
        # Convert to numpy
        if isinstance(X, pd.DataFrame):
            X = X.values
        else:
            X = np.asarray(X)
        
        if y is not None:
            y = np.asarray(y)
        
        # Scale features
        if self.scale_features and self.scaler_ is not None:
            X = self.scaler_.transform(X)
        
        # Remove outliers
        if self.remove_outliers and y is not None:
            X, y = self._remove_outliers(X, y)
        
        if y is not None:
            return X, y
        return X
    
    def fit_transform(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[Union[np.ndarray, pd.Series]] = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, Optional[np.ndarray]]]:
        """Fit and transform in one step."""
        return self.fit(X, y).transform(X, y)
    
    def _remove_outliers(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Remove outliers using Z-score threshold.
        
        Outliers are detected separately for each class to preserve
        class distribution.
        
        Parameters
        ----------
        X : ndarray
            Features
        y : ndarray
            Labels
            
        Returns
        -------
        X_clean : ndarray
            Features without outliers
        y_clean : ndarray
            Labels without outliers
        """
        if not self.remove_outliers:
            return X, y
        
        outlier_mask = np.zeros(len(X), dtype=bool)
        
        # Process each class separately
        for label in np.unique(y):
            class_mask = (y == label)
            X_class = X[class_mask]
            
            # Compute Z-scores
            z_scores = np.abs((X_class - np.mean(X_class, axis=0)) / 
                             (np.std(X_class, axis=0) + 1e-10))
            
            # Mark outliers (samples with any feature beyond threshold)
            class_outliers = np.any(z_scores > self.z_score_threshold, axis=1)
            
            # Update global mask
            class_indices = np.where(class_mask)[0]
            outlier_mask[class_indices[class_outliers]] = True
        
        # Remove outliers
        clean_mask = ~outlier_mask
        X_clean = X[clean_mask]
        y_clean = y[clean_mask]
        
        self.n_outliers_removed_ = np.sum(outlier_mask)
        
        return X_clean, y_clean
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str,
        feature_cols: Optional[List[str]] = None,
        test_size: float = 0.2,
        val_size: float = 0.1,
        stratify: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Complete data preparation pipeline.
        
        Parameters
        ----------
        df : DataFrame
            Raw data
        target_col : str
            Name of target column
        feature_cols : list, optional
            Names of feature columns (None = all except target)
        test_size : float, default=0.2
            Proportion of test set
        val_size : float, default=0.1
            Proportion of validation set (from training set)
        stratify : bool, default=True
            Whether to stratify splits
            
        Returns
        -------
        data : dict
            Dictionary containing:
                - X_train, y_train: Training data
                - X_val, y_val: Validation data  
                - X_test, y_test: Test data
                - scaler: Fitted scaler
        """
        # Extract features and target
        if feature_cols is None:
            feature_cols = [c for c in df.columns if c != target_col]
        
        X = df[feature_cols].values
        y = df[target_col].values
        
        # Encode labels if needed (convert to 0/1)
        if y.dtype == object or len(np.unique(y)) > 2:
            # For binary classification, ensure minority is 1
            unique_labels = np.unique(y)
            if len(unique_labels) == 2:
                counts = [np.sum(y == label) for label in unique_labels]
                minority_label = unique_labels[np.argmin(counts)]
                y = (y == minority_label).astype(int)
            else:
                raise ValueError(f"Expected binary classification, got {len(unique_labels)} classes")
        
        # First split: separate test set
        stratify_y = y if stratify else None
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=stratify_y,
            random_state=self.random_state
        )
        
        # Second split: separate validation from training
        if val_size > 0:
            val_ratio = val_size / (1 - test_size)
            stratify_y_temp = y_temp if stratify else None
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp,
                test_size=val_ratio,
                stratify=stratify_y_temp,
                random_state=self.random_state
            )
        else:
            X_train, y_train = X_temp, y_temp
            X_val, y_val = None, None
        
        # Fit preprocessor on training data only
        self.fit(X_train)
        
        # Transform all splits
        X_train, y_train = self.transform(X_train, y_train)
        if X_val is not None:
            X_val = self.transform(X_val)  # Don't remove outliers from val
        X_test = self.transform(X_test)  # Don't remove outliers from test
        
        result = {
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test,
            'y_test': y_test,
            'scaler': self.scaler_,
            'feature_names': self.feature_names_
        }
        
        if X_val is not None:
            result['X_val'] = X_val
            result['y_val'] = y_val
        
        return result


def load_german_credit(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load German Credit dataset.
    
    Parameters
    ----------
    path : str, optional
        Path to data file (default: Data/raw/german_credit/german.data)
        
    Returns
    -------
    df : DataFrame
        Processed dataset with proper column names
    """
    if path is None:
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'Data', 'raw', 'german_credit', 'german.data'
        )
    
    # Define column names (from UCI documentation)
    columns = [
        'checking_status', 'duration', 'credit_history', 'purpose',
        'credit_amount', 'savings_status', 'employment', 'installment_rate',
        'personal_status', 'other_parties', 'residence_since', 'property_magnitude',
        'age', 'other_payment_plans', 'housing', 'existing_credits', 'job',
        'num_dependents', 'own_telephone', 'foreign_worker', 'class'
    ]
    
    # Load data
    df = pd.read_csv(path, sep=' ', header=None, names=columns)
    
    # Convert target: 1 (good) -> 0, 2 (bad) -> 1 (minority = bad credit)
    df['class'] = df['class'] - 1
    
    return df


def load_default_credit_card(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load Default of Credit Card Clients dataset.
    
    Parameters
    ----------
    path : str, optional
        Path to Excel file
        
    Returns
    -------
    df : DataFrame
        Processed dataset
    """
    if path is None:
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'Data', 'raw', 'default_credit_card',
            'default_of_credit_card_clients.xls'
        )
    
    # Load Excel (header is in second row)
    df = pd.read_excel(path, header=1)
    
    # Rename target column for consistency
    df = df.rename(columns={'default payment next month': 'class'})
    
    return df
