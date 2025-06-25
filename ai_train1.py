from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
import joblib

X, y = make_regression(n_samples=100, n_features=1, noise=0.1)
model = LinearRegression()
model.fit(X, y)

joblib.dump(model, 'linear_model.pkl')
print('save ok!')