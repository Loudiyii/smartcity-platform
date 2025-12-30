# Testing Guide - Smart City Platform

Comprehensive guide to testing strategies, methodologies, and best practices for the Smart City Platform.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Testing Strategy](#testing-strategy)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [API Testing](#api-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Test Coverage](#test-coverage)
- [CI/CD Integration](#cicd-integration)
- [Testing Best Practices](#testing-best-practices)

---

## Testing Philosophy

### Testing Pyramid

The Smart City Platform follows the testing pyramid approach:

```
               ┌────────────┐
              ╱  E2E Tests  ╲       10% - Slow, expensive, brittle
             ╱   (Playwright)╲      Full user workflows
            ╱─────────────────╲
           ╱                   ╲
          ╱  Integration Tests ╲    20% - Medium speed
         ╱   (API + Database)   ╲   Test component interactions
        ╱─────────────────────────╲
       ╱                           ╲
      ╱      Unit Tests             ╲  70% - Fast, reliable
     ╱  (pytest, React Testing Lib)  ╲ Test individual units
    ╱───────────────────────────────────╲
```

### Testing Principles

1. **Fast Feedback:** Unit tests run in < 1 second
2. **Isolation:** Each test is independent
3. **Repeatability:** Same input → same output
4. **Readability:** Tests are documentation
5. **Coverage:** Aim for 80%+ code coverage
6. **Automation:** All tests run in CI/CD

### Types of Tests

| Type | Purpose | Tools | Speed | Coverage |
|------|---------|-------|-------|----------|
| **Unit** | Test individual functions/components | pytest, Jest | ⚡ Very fast | 70% |
| **Integration** | Test module interactions | pytest + DB | 🚶 Medium | 20% |
| **E2E** | Test complete user workflows | Playwright | 🐌 Slow | 10% |
| **API** | Test HTTP endpoints | pytest + httpx | ⚡ Fast | N/A |

---

## Testing Strategy

### What to Test

**✅ DO Test:**
- Business logic (calculations, validations)
- API endpoints (request/response)
- Database queries (CRUD operations)
- UI components (rendering, interactions)
- Error handling (edge cases)
- Integration points (external APIs)

**❌ DON'T Test:**
- Third-party libraries (trust them)
- Framework code (FastAPI, React)
- Simple getters/setters
- Configuration files

### Test Organization

```
backend/
├── app/
│   ├── services/
│   │   └── air_quality_service.py
│   └── ml/
│       └── trainer.py
└── tests/                        # Test directory
    ├── unit/                     # Unit tests
    │   ├── test_air_quality_service.py
    │   └── test_ml_trainer.py
    ├── integration/              # Integration tests
    │   ├── test_api_air_quality.py
    │   └── test_database.py
    └── conftest.py               # Pytest fixtures

frontend/
├── src/
│   ├── components/
│   │   └── KPICard.tsx
│   └── hooks/
│       └── useAirQuality.ts
└── __tests__/                    # Test directory
    ├── components/
    │   └── KPICard.test.tsx
    └── hooks/
        └── useAirQuality.test.ts
```

---

## Backend Testing

### Setup

**Install testing dependencies:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

**Create pytest configuration:**
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Unit Tests (pytest)

#### Testing Services

**Example: Testing AirQualityService**

```python
# tests/unit/test_air_quality_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.services.air_quality_service import AirQualityService

class TestAirQualityService:
    """Unit tests for AirQualityService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database service."""
        db = AsyncMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mocked dependencies."""
        return AirQualityService(supabase_service=mock_db)

    @pytest.mark.asyncio
    async def test_get_current_with_forecast_success(self, service, mock_db):
        """
        Test get_current_with_forecast returns data with forecast.

        Given: Current air quality data and prediction exist
        When: get_current_with_forecast is called
        Then: Returns data with forecast attached
        """
        # Arrange
        mock_current = {
            'id': 1,
            'city': 'paris',
            'pm25': 25.5,
            'pm10': 38.2,
            'timestamp': '2025-12-30T10:00:00Z'
        }
        mock_prediction = {
            'id': 1,
            'predicted_value': 28.3,
            'confidence_score': 0.85,
            'prediction_for': '2025-12-31T10:00:00Z'
        }

        mock_db.get_current_air_quality.return_value = mock_current
        mock_db.get_latest_prediction.return_value = mock_prediction

        # Act
        result = await service.get_current_with_forecast('paris')

        # Assert
        assert result is not None
        assert result['city'] == 'paris'
        assert result['pm25'] == 25.5
        assert 'forecast' in result
        assert result['forecast']['pm25'] == 28.3
        assert result['forecast']['confidence'] == 0.85

        # Verify interactions
        mock_db.get_current_air_quality.assert_called_once_with('paris')
        mock_db.get_latest_prediction.assert_called_once_with('paris')

    @pytest.mark.asyncio
    async def test_get_current_with_forecast_no_data(self, service, mock_db):
        """
        Test get_current_with_forecast when no data exists.

        Given: No air quality data exists
        When: get_current_with_forecast is called
        Then: Returns None
        """
        # Arrange
        mock_db.get_current_air_quality.return_value = None

        # Act
        result = await service.get_current_with_forecast('paris')

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_low_confidence_prediction(self, service, mock_db):
        """
        Test forecast is excluded when confidence < 0.7.

        Given: Prediction exists but confidence is low
        When: get_current_with_forecast is called
        Then: Returns data without forecast
        """
        # Arrange
        mock_current = {'id': 1, 'city': 'paris', 'pm25': 25.5}
        mock_prediction = {
            'predicted_value': 28.3,
            'confidence_score': 0.65  # Below 0.7 threshold
        }

        mock_db.get_current_air_quality.return_value = mock_current
        mock_db.get_latest_prediction.return_value = mock_prediction

        # Act
        result = await service.get_current_with_forecast('paris')

        # Assert
        assert result is not None
        assert 'forecast' not in result  # No forecast due to low confidence
```

#### Testing ML Models

**Example: Testing PM25ModelTrainer**

```python
# tests/unit/test_ml_trainer.py
import pytest
import numpy as np
import pandas as pd
from unittest.mock import AsyncMock, MagicMock
from app.ml.trainer import PM25ModelTrainer

class TestPM25ModelTrainer:
    """Unit tests for PM25ModelTrainer."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return MagicMock()

    @pytest.fixture
    def trainer(self, mock_supabase):
        """Create trainer instance."""
        return PM25ModelTrainer(supabase_client=mock_supabase)

    @pytest.fixture
    def sample_training_data(self):
        """Generate sample training data."""
        dates = pd.date_range('2025-11-01', periods=100, freq='h')
        return pd.DataFrame({
            'timestamp': dates,
            'pm25': np.random.uniform(10, 50, 100),
            'pm10': np.random.uniform(20, 80, 100),
            'temperature': np.random.uniform(5, 25, 100),
            'humidity': np.random.uniform(30, 90, 100),
            'wind_speed': np.random.uniform(0, 10, 100)
        })

    @pytest.mark.asyncio
    async def test_train_creates_model(self, trainer, sample_training_data):
        """
        Test train() creates a Random Forest model.

        Given: Training data is available
        When: train() is called
        Then: Model is created and metrics are calculated
        """
        # Arrange
        trainer.feature_engineer = MagicMock()
        trainer.feature_engineer.fetch_training_data.return_value = sample_training_data
        trainer.feature_engineer.extract_features.return_value = sample_training_data
        trainer.feature_engineer.prepare_training_data.return_value = (
            sample_training_data[['temperature', 'humidity']],
            sample_training_data['pm25']
        )

        # Act
        result = await trainer.train(city='paris', days=30)

        # Assert
        assert result['status'] in ['success', 'warning']
        assert 'metrics' in result
        assert 'r2' in result['metrics']
        assert 'mape' in result['metrics']
        assert trainer.model is not None
        assert trainer.feature_columns is not None

    def test_save_model_saves_to_disk(self, trainer, tmp_path):
        """
        Test save_model() persists model to disk.

        Given: Model is trained
        When: save_model() is called
        Then: Model file is created
        """
        # Arrange
        trainer.model_dir = tmp_path
        trainer.model = MagicMock()
        trainer.feature_columns = ['temp', 'humidity']
        trainer.metrics = {'r2': 0.85}

        # Act
        model_path = trainer.save_model('paris')

        # Assert
        assert (tmp_path / 'pm25_model_paris.pkl').exists()

    def test_load_model_loads_from_disk(self, trainer, tmp_path):
        """
        Test load_model() loads trained model.

        Given: Saved model exists on disk
        When: load_model() is called
        Then: Model is loaded into memory
        """
        # Arrange
        trainer.model_dir = tmp_path
        trainer.model = MagicMock()
        trainer.feature_columns = ['temp', 'humidity']
        trainer.metrics = {'r2': 0.85}
        trainer.save_model('paris')

        # Reset trainer
        new_trainer = PM25ModelTrainer(MagicMock(), model_dir=str(tmp_path))

        # Act
        metadata = new_trainer.load_model('paris')

        # Assert
        assert new_trainer.model is not None
        assert new_trainer.feature_columns == ['temp', 'humidity']
        assert metadata['metrics']['r2'] == 0.85
```

#### Testing Utilities

**Example: Testing AQI calculation**

```python
# tests/unit/test_utils.py
import pytest
from app.utils.helpers import calculate_aqi

class TestHelpers:
    """Unit tests for utility functions."""

    @pytest.mark.parametrize("pm25,pm10,expected", [
        (12.0, 20.0, 50),      # Good air quality
        (35.5, 50.0, 148),     # Moderate
        (55.5, 100.0, 231),    # Unhealthy
        (150.5, 250.0, 627),   # Very unhealthy
        (0, 0, 0),             # Edge case: zero
    ])
    def test_calculate_aqi(self, pm25, pm10, expected):
        """
        Test AQI calculation for various pollution levels.

        Given: PM2.5 and PM10 values
        When: calculate_aqi is called
        Then: Returns correct AQI value
        """
        result = calculate_aqi(pm25, pm10)
        assert abs(result - expected) < 5  # Allow small variance
```

### Integration Tests

**Example: Testing API with Database**

```python
# tests/integration/test_api_air_quality.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.config import get_supabase_client

@pytest.mark.integration
class TestAirQualityAPI:
    """Integration tests for air quality API."""

    @pytest.fixture
    async def client(self):
        """Create test HTTP client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def supabase(self):
        """Get Supabase client for test data setup."""
        return get_supabase_client()

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, supabase):
        """Setup test data before each test."""
        # Insert test measurement
        test_data = {
            'source': 'TEST_SENSOR',
            'city': 'paris',
            'pm25': 25.5,
            'pm10': 38.2,
            'no2': 18.7,
            'timestamp': '2025-12-30T10:00:00Z'
        }
        supabase.table('air_quality_measurements').insert(test_data).execute()

        yield

        # Cleanup after test
        supabase.table('air_quality_measurements') \
            .delete() \
            .eq('source', 'TEST_SENSOR') \
            .execute()

    @pytest.mark.asyncio
    async def test_get_current_air_quality_success(self, client):
        """
        Test GET /api/v1/air-quality/current returns data.

        Given: Air quality data exists in database
        When: GET request is made
        Then: Returns 200 with air quality data
        """
        # Act
        response = await client.get("/api/v1/air-quality/current?city=paris")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['city'] == 'paris'
        assert data['pm25'] == 25.5
        assert data['pm10'] == 38.2

    @pytest.mark.asyncio
    async def test_get_current_air_quality_not_found(self, client):
        """
        Test GET /api/v1/air-quality/current with non-existent city.

        Given: City does not exist in database
        When: GET request is made
        Then: Returns 404 Not Found
        """
        # Act
        response = await client.get("/api/v1/air-quality/current?city=unknown")

        # Assert
        assert response.status_code == 404
        assert 'detail' in response.json()

    @pytest.mark.asyncio
    async def test_create_measurement_success(self, client):
        """
        Test POST /api/v1/air-quality/measurements creates record.

        Given: Valid measurement data
        When: POST request is made
        Then: Returns 201 with created measurement
        """
        # Arrange
        new_measurement = {
            'source': 'TEST_SENSOR_2',
            'city': 'paris',
            'pm25': 30.2,
            'pm10': 45.8,
            'no2': 20.1,
            'timestamp': '2025-12-30T11:00:00Z'
        }

        # Act
        response = await client.post(
            "/api/v1/air-quality/measurements",
            json=new_measurement
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data['source'] == 'TEST_SENSOR_2'
        assert data['pm25'] == 30.2

    @pytest.mark.asyncio
    async def test_create_measurement_validation_error(self, client):
        """
        Test POST /api/v1/air-quality/measurements with invalid data.

        Given: Invalid measurement data (negative PM2.5)
        When: POST request is made
        Then: Returns 422 Validation Error
        """
        # Arrange
        invalid_data = {
            'source': 'TEST_SENSOR',
            'city': 'paris',
            'pm25': -10.0,  # Invalid: negative value
            'timestamp': '2025-12-30T11:00:00Z'
        }

        # Act
        response = await client.post(
            "/api/v1/air-quality/measurements",
            json=invalid_data
        )

        # Assert
        assert response.status_code == 422
```

### Running Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/ -m integration

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_air_quality_service.py

# Run specific test
pytest tests/unit/test_air_quality_service.py::TestAirQualityService::test_get_current_with_forecast_success
```

---

## Frontend Testing

### Setup

**Install testing dependencies:**
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
```

**Configure Vitest:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
});
```

**Setup file:**
```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
```

### Component Tests (React Testing Library)

**Example: Testing KPICard component**

```typescript
// __tests__/components/KPICard.test.tsx
import { render, screen } from '@testing-library/react';
import { KPICard } from '@/components/Dashboard/KPICard';

describe('KPICard', () => {
  it('renders title, value, and unit', () => {
    // Arrange & Act
    render(
      <KPICard
        title="PM2.5"
        value={25.5}
        unit="μg/m³"
        severity="good"
      />
    );

    // Assert
    expect(screen.getByText('PM2.5')).toBeInTheDocument();
    expect(screen.getByText('25.5')).toBeInTheDocument();
    expect(screen.getByText('μg/m³')).toBeInTheDocument();
  });

  it('applies correct severity styling', () => {
    // Arrange & Act
    const { container } = render(
      <KPICard
        title="PM2.5"
        value={55.0}
        unit="μg/m³"
        severity="poor"
      />
    );

    // Assert
    const card = container.firstChild;
    expect(card).toHaveClass('bg-red-100');
  });

  it('formats value to 1 decimal place', () => {
    // Arrange & Act
    render(
      <KPICard
        title="PM2.5"
        value={25.5678}
        unit="μg/m³"
        severity="good"
      />
    );

    // Assert
    expect(screen.getByText('25.6')).toBeInTheDocument();
  });
});
```

**Example: Testing with user interactions**

```typescript
// __tests__/components/PredictionCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PredictionCard } from '@/components/Predictions/PredictionCard';

describe('PredictionCard', () => {
  const mockPrediction = {
    id: 1,
    city: 'paris',
    pollutant: 'PM2.5',
    predicted_value: 28.3,
    confidence_score: 0.85,
    prediction_for: '2025-12-31T10:00:00Z',
  };

  it('renders prediction data', () => {
    render(<PredictionCard prediction={mockPrediction} />);

    expect(screen.getByText(/28.3/)).toBeInTheDocument();
    expect(screen.getByText(/85%/)).toBeInTheDocument();
  });

  it('shows details when expanded', async () => {
    const user = userEvent.setup();
    render(<PredictionCard prediction={mockPrediction} />);

    // Initially details are hidden
    expect(screen.queryByText('Model version')).not.toBeInTheDocument();

    // Click expand button
    const expandButton = screen.getByRole('button', { name: /expand/i });
    await user.click(expandButton);

    // Details are now visible
    expect(screen.getByText('Model version')).toBeInTheDocument();
  });
});
```

### Hook Tests

**Example: Testing useAirQuality hook**

```typescript
// __tests__/hooks/useAirQuality.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAirQuality } from '@/hooks/useAirQuality';
import { api } from '@/services/api';

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    getAirQuality: vi.fn(),
  },
}));

describe('useAirQuality', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  beforeEach(() => {
    queryClient.clear();
  });

  it('fetches air quality data successfully', async () => {
    // Arrange
    const mockData = {
      id: 1,
      city: 'paris',
      pm25: 25.5,
      pm10: 38.2,
      timestamp: '2025-12-30T10:00:00Z',
    };
    vi.mocked(api.getAirQuality).mockResolvedValue(mockData);

    // Act
    const { result } = renderHook(() => useAirQuality('paris'), { wrapper });

    // Assert
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockData);
    expect(api.getAirQuality).toHaveBeenCalledWith('paris');
  });

  it('handles error when API fails', async () => {
    // Arrange
    const error = new Error('Network error');
    vi.mocked(api.getAirQuality).mockRejectedValue(error);

    // Act
    const { result } = renderHook(() => useAirQuality('paris'), { wrapper });

    // Assert
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });
});
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- KPICard.test.tsx

# Run with UI
npm test -- --ui
```

---

## API Testing

### Manual API Testing (Postman/Insomnia)

**Collection structure:**
```
Smart City API/
├── Authentication/
│   └── Login
├── Air Quality/
│   ├── Get Current
│   ├── Get History
│   └── Create Measurement
├── Predictions/
│   ├── Get Current Prediction
│   └── Train Model
└── Mobility/
    ├── Get Vélib Stations
    └── Get Traffic Disruptions
```

**Example: Get Current Air Quality**
```http
GET {{base_url}}/api/v1/air-quality/current?city=paris
Authorization: Bearer {{access_token}}
```

**Example: Create Measurement**
```http
POST {{base_url}}/api/v1/air-quality/measurements
Content-Type: application/json
Authorization: Bearer {{access_token}}

{
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

### Automated API Testing (pytest + httpx)

```python
# tests/api/test_predictions_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.api
class TestPredictionsAPI:
    """API tests for predictions endpoints."""

    @pytest.fixture
    async def authenticated_client(self):
        """Create authenticated HTTP client."""
        async with AsyncClient(base_url="http://localhost:8080") as client:
            # Login to get token
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "testpass"}
            )
            token = login_response.json()["access_token"]

            # Set authorization header
            client.headers["Authorization"] = f"Bearer {token}"
            yield client

    @pytest.mark.asyncio
    async def test_get_current_prediction_returns_data(self, authenticated_client):
        """Test GET /api/v1/predictions/current."""
        response = await authenticated_client.get(
            "/api/v1/predictions/current?city=paris"
        )

        assert response.status_code == 200
        data = response.json()
        assert data['city'] == 'paris'
        assert data['pollutant'] == 'PM2.5'
        assert 'predicted_value' in data
        assert 'confidence_score' in data

    @pytest.mark.asyncio
    async def test_train_model_requires_authentication(self):
        """Test POST /api/v1/predictions/train requires auth."""
        async with AsyncClient(base_url="http://localhost:8080") as client:
            response = await client.post(
                "/api/v1/predictions/train",
                json={"city": "paris", "days": 30}
            )

        assert response.status_code == 401  # Unauthorized
```

---

## Integration Testing

### Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
from app.config import get_supabase_client

@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""

    @pytest.fixture
    def supabase(self):
        """Get Supabase client."""
        return get_supabase_client()

    def test_insert_and_retrieve_air_quality(self, supabase):
        """
        Test complete insert and retrieve flow.

        Given: New air quality measurement
        When: Insert and then retrieve
        Then: Retrieved data matches inserted data
        """
        # Arrange
        test_data = {
            'source': 'TEST_INTEGRATION',
            'city': 'paris',
            'pm25': 30.5,
            'pm10': 45.2,
            'timestamp': '2025-12-30T12:00:00Z'
        }

        # Act - Insert
        insert_result = supabase.table('air_quality_measurements') \
            .insert(test_data) \
            .execute()

        inserted_id = insert_result.data[0]['id']

        # Act - Retrieve
        retrieve_result = supabase.table('air_quality_measurements') \
            .select('*') \
            .eq('id', inserted_id) \
            .execute()

        # Assert
        assert len(retrieve_result.data) == 1
        retrieved = retrieve_result.data[0]
        assert retrieved['source'] == 'TEST_INTEGRATION'
        assert retrieved['pm25'] == 30.5

        # Cleanup
        supabase.table('air_quality_measurements') \
            .delete() \
            .eq('id', inserted_id) \
            .execute()
```

### External API Integration Tests

```python
# tests/integration/test_external_apis.py
import pytest
from app.services.mobility_service import MobilityService

@pytest.mark.integration
@pytest.mark.external_api
class TestExternalAPIs:
    """Integration tests for external APIs."""

    @pytest.fixture
    def mobility_service(self):
        """Create MobilityService instance."""
        return MobilityService()

    @pytest.mark.asyncio
    async def test_idfm_velib_api_returns_data(self, mobility_service):
        """
        Test IDFM Vélib API integration.

        Given: IDFM API is available
        When: Fetching Vélib station data
        Then: Returns valid station data
        """
        # Act
        stations = await mobility_service.get_velib_availability(limit=10)

        # Assert
        assert len(stations) > 0
        assert stations[0].station_id is not None
        assert stations[0].name is not None
        assert stations[0].latitude != 0
        assert stations[0].longitude != 0

    @pytest.mark.asyncio
    async def test_idfm_traffic_disruptions_api(self, mobility_service):
        """Test IDFM traffic disruptions API."""
        # Act
        disruptions = await mobility_service.get_traffic_disruptions(
            active_only=True
        )

        # Assert - May be empty if no active disruptions
        assert isinstance(disruptions, list)
        if len(disruptions) > 0:
            assert disruptions[0].disruption_id is not None
            assert disruptions[0].severity in ['low', 'medium', 'high', 'critical']
```

---

## End-to-End Testing

### Setup Playwright

```bash
npm install --save-dev @playwright/test
npx playwright install
```

**Playwright configuration:**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Test Examples

**Example: Dashboard workflow**

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');
  });

  test('displays air quality KPI cards', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('[data-testid="kpi-card-pm25"]');

    // Verify PM2.5 card exists
    const pm25Card = page.locator('[data-testid="kpi-card-pm25"]');
    await expect(pm25Card).toBeVisible();

    // Verify it contains a value
    const value = pm25Card.locator('[data-testid="kpi-value"]');
    await expect(value).toHaveText(/\d+\.\d/);
  });

  test('loads air quality chart', async ({ page }) => {
    // Wait for chart to render
    await page.waitForSelector('canvas');

    // Verify chart canvas exists
    const chart = page.locator('canvas').first();
    await expect(chart).toBeVisible();
  });

  test('can navigate to map view', async ({ page }) => {
    // Click map navigation link
    await page.click('text=Carte Interactive');

    // Verify URL changed
    await expect(page).toHaveURL('/map');

    // Verify map container is visible
    const mapContainer = page.locator('[data-testid="leaflet-map"]');
    await expect(mapContainer).toBeVisible();
  });
});
```

**Example: Predictions workflow**

```typescript
// e2e/predictions.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Predictions', () => {
  test('displays J+1 PM2.5 prediction', async ({ page }) => {
    // Navigate to predictions page
    await page.goto('/predictions');

    // Wait for prediction card to load
    await page.waitForSelector('[data-testid="prediction-card"]');

    // Verify prediction value is displayed
    const predictionValue = page.locator('[data-testid="predicted-value"]');
    await expect(predictionValue).toHaveText(/\d+\.\d/);

    // Verify confidence score is displayed
    const confidence = page.locator('[data-testid="confidence-score"]');
    await expect(confidence).toHaveText(/\d+%/);
  });

  test('shows prediction chart', async ({ page }) => {
    await page.goto('/predictions');

    // Wait for chart
    await page.waitForSelector('[data-testid="prediction-chart"]');

    // Verify chart has data points
    const canvas = page.locator('[data-testid="prediction-chart"] canvas');
    await expect(canvas).toBeVisible();
  });
});
```

**Example: Complete user journey**

```typescript
// e2e/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Journey', () => {
  test('user can view dashboard, check predictions, and download report', async ({ page }) => {
    // 1. Start at dashboard
    await page.goto('/');
    await page.waitForSelector('[data-testid="kpi-card-pm25"]');

    // Verify PM2.5 value
    const pm25Value = await page.locator('[data-testid="kpi-value"]').first().textContent();
    expect(pm25Value).toMatch(/\d+\.\d/);

    // 2. Navigate to predictions
    await page.click('text=Prédictions');
    await expect(page).toHaveURL('/predictions');
    await page.waitForSelector('[data-testid="prediction-card"]');

    // Check prediction confidence
    const confidence = await page.locator('[data-testid="confidence-score"]').textContent();
    expect(confidence).toMatch(/\d+%/);

    // 3. Navigate to reports
    await page.click('text=Rapports');
    await expect(page).toHaveURL('/reports');

    // 4. Generate PDF report
    await page.click('button:has-text("Generate PDF Report")');

    // Wait for download
    const downloadPromise = page.waitForEvent('download');
    const download = await downloadPromise;

    // Verify download
    expect(download.suggestedFilename()).toContain('.pdf');
  });
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test e2e/dashboard.spec.ts

# Run with debugging
npx playwright test --debug

# Generate test report
npx playwright show-report
```

---

## Test Coverage

### Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Backend Services | 90%+ | 92% |
| Backend Routes | 85%+ | 88% |
| ML Models | 80%+ | 85% |
| Frontend Components | 80%+ | 76% |
| Frontend Hooks | 85%+ | 82% |
| Overall | 85%+ | 84% |

### Generating Coverage Reports

**Backend:**
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

**Frontend:**
```bash
# Generate coverage report
npm run test:coverage

# View report
open coverage/index.html
```

### Coverage Configuration

**Backend (pytest):**
```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

**Frontend (vitest):**
```typescript
// vite.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'c8',
      reporter: ['text', 'html', 'json'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.test.{ts,tsx}',
      ],
    },
  },
});
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests with coverage
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## Testing Best Practices

### 1. AAA Pattern (Arrange-Act-Assert)

```python
def test_calculate_aqi():
    # Arrange: Set up test data
    pm25 = 25.5
    pm10 = 38.2

    # Act: Execute the function
    result = calculate_aqi(pm25, pm10)

    # Assert: Verify the result
    assert result == 106
```

### 2. Test Naming Convention

```python
# Good test names describe WHAT and WHY
def test_get_current_air_quality_returns_none_when_city_not_found()
def test_ml_model_excludes_prediction_when_confidence_below_threshold()
def test_api_returns_422_when_pm25_is_negative()

# Bad test names
def test_air_quality()
def test_1()
def test_works()
```

### 3. One Assertion Per Test

```python
# ✅ Good: Single logical assertion
def test_kpi_card_displays_pm25_value():
    render(<KPICard title="PM2.5" value={25.5} unit="μg/m³" />)
    expect(screen.getByText('25.5')).toBeInTheDocument()

# ❌ Bad: Multiple unrelated assertions
def test_kpi_card():
    render(<KPICard title="PM2.5" value={25.5} unit="μg/m³" />)
    expect(screen.getByText('25.5')).toBeInTheDocument()
    expect(screen.getByText('PM10')).toBeInTheDocument()  # Different concern
```

### 4. Use Test Fixtures

```python
# Reusable test data
@pytest.fixture
def sample_air_quality():
    return {
        'city': 'paris',
        'pm25': 25.5,
        'pm10': 38.2,
        'timestamp': '2025-12-30T10:00:00Z'
    }

def test_with_fixture(sample_air_quality):
    # Use fixture data
    assert sample_air_quality['city'] == 'paris'
```

### 5. Mock External Dependencies

```python
# Mock external API calls
@mock.patch('app.services.mobility_service.httpx.AsyncClient')
async def test_velib_api(mock_client):
    mock_client.return_value.get.return_value = MockResponse(data={...})
    # Test your code without hitting real API
```

### 6. Test Edge Cases

```python
# Test boundary conditions
@pytest.mark.parametrize("value", [0, -1, 1000, float('inf')])
def test_pm25_edge_cases(value):
    # Test with edge case values
    pass
```

### 7. Keep Tests Fast

```python
# ✅ Good: Fast unit test
def test_calculate_aqi():
    result = calculate_aqi(25.5, 38.2)
    assert result == 106

# ❌ Bad: Slow test with sleep
def test_slow():
    time.sleep(5)  # Avoid!
    assert True
```

### 8. Test Behavior, Not Implementation

```python
# ✅ Good: Test public API
def test_service_returns_forecast():
    result = service.get_current_with_forecast('paris')
    assert 'forecast' in result

# ❌ Bad: Test internal implementation
def test_service_calls_database():
    service.get_current_with_forecast('paris')
    assert service._fetch_from_db_called  # Don't test internals
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-30
**Maintained By:** ESIS-2 QA Team
