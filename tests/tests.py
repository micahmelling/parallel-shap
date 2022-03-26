import os
import shutil

import pandas as pd
import pytest
import shap
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.ensemble import (ExtraTreesClassifier, ExtraTreesRegressor,
                              GradientBoostingClassifier,
                              GradientBoostingRegressor,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.linear_model import (ElasticNet, Lasso, LinearRegression,
                                  LogisticRegression, Ridge)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor

from auto_shap.auto_shap import (generate_shap_values,
                                 produce_shap_values_and_summary_plots)


def train_simple_classification_model(model):
    x, y = load_breast_cancer(return_X_y=True, as_frame=True)
    model.fit(x, y)
    x = x.head(50)
    return model, x


def train_simple_regression_model(model):
    x, y = load_diabetes(return_X_y=True, as_frame=True)
    model.fit(x, y)
    x = x.head(50)
    return model, x


@pytest.fixture
def random_forest_classifier_and_data():
    return train_simple_classification_model(RandomForestClassifier())


@pytest.fixture
def extra_trees_classifier_and_data():
    return train_simple_classification_model(ExtraTreesClassifier())


@pytest.fixture
def logistic_regression_classifier_and_data():
    return train_simple_classification_model(LogisticRegression())


@pytest.fixture
def gradient_boosting_classifier_and_data():
    return train_simple_classification_model(GradientBoostingClassifier())


@pytest.fixture
def xgboost_classifier_and_data():
    return train_simple_classification_model(XGBClassifier(n_jobs=1))


@pytest.fixture
def lightgbm_classifier_and_data():
    return train_simple_classification_model(LGBMClassifier())


@pytest.fixture
def catboost_classifier_and_data():
    return train_simple_classification_model(CatBoostClassifier(iterations=10))


@pytest.fixture
def decision_tree_classifier_and_data():
    return train_simple_regression_model(DecisionTreeClassifier())


@pytest.fixture
def ridge_regressor_and_data():
    return train_simple_regression_model(Ridge())


@pytest.fixture
def lasso_regressor_and_data():
    return train_simple_regression_model(Lasso())


@pytest.fixture
def elastic_net_regressor_and_data():
    return train_simple_regression_model(ElasticNet())


@pytest.fixture
def linear_regression_and_data():
    return train_simple_regression_model(LinearRegression())


@pytest.fixture
def decision_tree_regressor_and_data():
    return train_simple_regression_model(DecisionTreeRegressor())


@pytest.fixture
def extra_trees_regressor_and_data():
    return train_simple_regression_model(ExtraTreesRegressor())


@pytest.fixture
def random_forest_regressor_and_data():
    return train_simple_regression_model(RandomForestRegressor())


@pytest.fixture
def gradient_boosting_regressor_and_data():
    return train_simple_regression_model(GradientBoostingRegressor())


@pytest.fixture
def xgb_regressor_and_data():
    return train_simple_regression_model(XGBRegressor(n_jobs=1))


@pytest.fixture
def catboost_regressor_and_data():
    return train_simple_regression_model(CatBoostRegressor(iterations=10))


@pytest.fixture
def lgbm_regressor_and_data():
    return train_simple_regression_model(LGBMRegressor())


@pytest.fixture
def extra_trees_calibrated_classifier_and_data():
    return train_simple_classification_model(CalibratedClassifierCV(base_estimator=ExtraTreesClassifier(), cv=3))


@pytest.fixture
def xgboost_calibrated_classifier_and_data():
    return train_simple_classification_model(CalibratedClassifierCV(base_estimator=XGBClassifier(n_jobs=1)))


def test_parallel_shap_accuracy_classification(random_forest_classifier_and_data):
    model, x_df = random_forest_classifier_and_data
    shap_values_parallel_df, shap_expected_parallel_value, _ = generate_shap_values(model, x_df)
    explainer = shap.TreeExplainer(model)
    shap_values_df = pd.DataFrame(explainer.shap_values(x_df)[1], columns=list(x_df))
    shap_values_parallel_df['sum'] = shap_values_parallel_df.sum(axis=1)
    shap_values_parallel_df = shap_values_parallel_df.sort_values(by=['sum'], ascending=True)
    shap_values_df['sum'] = shap_values_df.sum(axis=1)
    shap_values_df = shap_values_df.sort_values(by=['sum'], ascending=True)
    assert shap_values_parallel_df['sum'].equals(shap_values_df['sum'])


def test_parallel_shap_accuracy_regression(extra_trees_regressor_and_data):
    model, x_df = extra_trees_regressor_and_data
    shap_values_parallel_df, shap_expected_parallel_value, _ = generate_shap_values(model, x_df)
    explainer = shap.TreeExplainer(model)
    shap_values_df = pd.DataFrame(explainer.shap_values(x_df), columns=list(x_df))
    shap_values_parallel_df['sum'] = shap_values_parallel_df.sum(axis=1)
    shap_values_parallel_df = shap_values_parallel_df.sort_values(by=['sum'], ascending=True)
    shap_values_df['sum'] = shap_values_df.sum(axis=1)
    shap_values_df = shap_values_df.sort_values(by=['sum'], ascending=True)
    assert shap_values_parallel_df['sum'].equals(shap_values_df['sum'])


def test_classification_random_forest_model(random_forest_classifier_and_data):
    model, x_df = random_forest_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_extra_trees_model(extra_trees_classifier_and_data):
    model, x_df = extra_trees_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_decision_tree_model(decision_tree_classifier_and_data):
    model, x_df = decision_tree_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_linear_model(logistic_regression_classifier_and_data):
    model, x_df = logistic_regression_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_gradient_boosting_model(gradient_boosting_classifier_and_data):
    model, x_df = gradient_boosting_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_xgboost_model(xgboost_classifier_and_data):
    model, x_df = xgboost_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_lightgbm_model(lightgbm_classifier_and_data):
    model, x_df = lightgbm_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_classification_catboost_model(catboost_classifier_and_data):
    model, x_df = catboost_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_ridge_model(ridge_regressor_and_data):
    model, x_df = ridge_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_lasso_model(lasso_regressor_and_data):
    model, x_df = lasso_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_elastic_net_model(elastic_net_regressor_and_data):
    model, x_df = elastic_net_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_linear_regression_model(linear_regression_and_data):
    model, x_df = linear_regression_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_decision_tree_model(decision_tree_regressor_and_data):
    model, x_df = decision_tree_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_extra_trees_model(extra_trees_regressor_and_data):
    model, x_df = extra_trees_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_random_forest_model(random_forest_regressor_and_data):
    model, x_df = random_forest_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_gradient_boosting_model(gradient_boosting_regressor_and_data):
    model, x_df = gradient_boosting_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_xgb_model(xgb_regressor_and_data):
    model, x_df = xgb_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_regression_catboost_model(catboost_regressor_and_data):
    model, x_df = catboost_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))


def test_regression_lgbm_model(lgbm_regressor_and_data):
    model, x_df = lgbm_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_kernel_shap_regression(gradient_boosting_regressor_and_data):
    model, x_df = gradient_boosting_regressor_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df, use_kernel=True)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_kernel_shap_classification(extra_trees_classifier_and_data):
    model, x_df = extra_trees_classifier_and_data
    x_df = x_df.head(10)
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df, use_kernel=True)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_calibrated_extra_trees_model(extra_trees_calibrated_classifier_and_data):
    model, x_df = extra_trees_calibrated_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_calibrated_extra_trees_model_with_kernel(extra_trees_calibrated_classifier_and_data):
    model, x_df = extra_trees_calibrated_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df, use_kernel=True)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_calibrated_xgboost_model(xgboost_calibrated_classifier_and_data):
    model, x_df = xgboost_calibrated_classifier_and_data
    shap_values_df, shap_expected_value, global_shap_df = generate_shap_values(model, x_df, use_kernel=True)
    assert len(shap_values_df) == len(x_df)
    assert len(global_shap_df) == len(list(x_df))
    assert isinstance(shap_expected_value, float)


def test_produce_shap_values_and_summary_plots_extra_trees_regressor(extra_trees_regressor_and_data):
    model, x_df = extra_trees_regressor_and_data
    produce_shap_values_and_summary_plots(model, x_df, 'etr_output')
    assert os.path.exists('etr_output/plots/shap_values_dot.png')


def test_produce_shap_values_and_summary_plots_random_forest_classifier(random_forest_classifier_and_data):
    model, x_df = random_forest_classifier_and_data
    produce_shap_values_and_summary_plots(model, x_df, 'rfc_output')
    assert os.path.exists('rfc_output/plots/shap_values_dot.png')


def test_produce_shap_values_and_summary_plots_lightgbm_classifier(lightgbm_classifier_and_data):
    model, x_df = lightgbm_classifier_and_data
    produce_shap_values_and_summary_plots(model, x_df, 'lgb_output')
    assert os.path.exists('lgb_output/plots/shap_values_dot.png')


def test_produce_shap_values_and_summary_plots_calibrated_classifier(extra_trees_calibrated_classifier_and_data):
    model, x_df = extra_trees_calibrated_classifier_and_data
    produce_shap_values_and_summary_plots(model, x_df, 'cc_output')
    assert os.path.exists('cc_output/plots/shap_values_dot.png')


def test_produce_shap_values_and_summary_plots_calibrated_classifier_with_kernel(extra_trees_calibrated_classifier_and_data):
    model, x_df = extra_trees_calibrated_classifier_and_data
    x_df = x_df.head(10)
    produce_shap_values_and_summary_plots(model, x_df, 'kcc_output', use_kernel=True)
    assert os.path.exists('kcc_output/plots/shap_values_dot.png')


def test_produce_shap_values_and_summary_plots_xgboost_classifier(xgboost_classifier_and_data):
    model, x_df = xgboost_classifier_and_data
    produce_shap_values_and_summary_plots(model, x_df, 'xgbc_output')
    assert os.path.exists('xgbc_output/plots/shap_values_dot.png')


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def remove_test_directories():
        directories = ['xgbc_output', 'kcc_output', 'cc_output', 'rfc_output', 'etr_output', 'lgb_output']
        for directory in directories:
            shutil.rmtree(directory)
    request.addfinalizer(remove_test_directories)
