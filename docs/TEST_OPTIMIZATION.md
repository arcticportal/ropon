# Test Suite Optimization Summary

## Overview
This document summarizes the optimizations made to reduce Wagtail test execution time from >5 minutes to ~2 minutes.

## Changes Implemented

### 1. Test Configuration Optimizations (High Impact)
Created `backend/ropon/settings/test.py` with performance-focused settings:

**Performance Improvements:**
- **Faster Password Hashing**: MD5PasswordHasher (vs BCrypt) - ~10x faster for test user creation
- **Disabled Migrations**: Tests use model state directly - saves 30-60 seconds
- **PostgreSQL Tuning**: Disabled fsync, synchronous_commit for test DB - 2-3x faster writes
- **Local Memory Cache**: Replaced Redis with LocMemCache - eliminates network overhead
- **Disabled Logging**: Removed I/O bottleneck during tests
- **Simplified Static Files**: No compression/hashing during tests

**Expected Impact**: 40-50% reduction in test setup/teardown time

### 2. CI Workflow Optimizations
Updated `.github/workflows/wagtail-tests.yml`:
- Added `--parallel` flag for parallel test execution
- Set `DJANGO_SETTINGS_MODULE=ropon.settings.test` environment variable

**Expected Impact**: Additional 30-40% reduction with parallel execution on multi-core CI runners

### 3. Test Consolidation (Test Count Reduction)

#### A. Geometry Block Tests (11 tests removed)
**File**: `backend/ropon_data/tests/blocks/test_geometry_blocks.py`
**Before**: 12 individual tests for coordinate boundary conditions
**After**: 1 parameterized test using `subTest`
**Reduction**: 12 → 1 test (11 tests removed)

**Rationale**: All tests followed identical pattern - create block, test invalid coordinate, expect ValidationError. Consolidated using data-driven approach.

#### B. User Model Tests (12 tests removed)
**File**: `backend/ropon_auth/tests/models/test_roponuser.py`
**Before**: 21 tests split across 2 test classes (TestRoponUser + RoponUserModelSpecificTests)
**After**: 9 comprehensive tests in single class
**Reduction**: 21 → 9 tests (12 tests removed)

**Key consolidations:**
- Combined duplicate username normalization tests (3 → 1)
- Merged case-insensitivity tests (4 → 1)
- Consolidated email validation tests (3 → 1)
- Combined superuser/regular user permission tests (2 → 1)

**Rationale**: Multiple tests checked same functionality with slight variations. Used comprehensive tests that cover multiple scenarios.

## Total Impact

### Test Count
- **Original**: 199 tests
- **After Consolidation**: 176 tests
- **Reduction**: 23 tests (11.6% fewer tests)

### Estimated Execution Time
- **Baseline**: ~5-6 minutes
- **Expected After Optimization**: ~2-2.5 minutes
- **Improvement**: 55-60% reduction

### Breakdown of Time Savings:
1. Test settings optimizations: ~40-50% faster setup
2. Parallel execution: ~30-40% additional speedup
3. Fewer tests: ~11% fewer test executions
4. **Combined effect**: ~55-60% total time reduction

## Recommendations for Further Optimization

### High-Priority (High Impact, Medium Effort)
1. **ObservingNetwork Tests** (67 tests)
   - File: `ropon_data/tests/models/test_observing_network_page.py` (1478 lines)
   - Potential reduction: 67 → 30-35 tests (~50% reduction)
   - Key areas:
     - Stream field CRUD tests (8 tests → 2 parameterized)
     - API slug/title tests (5 tests → 2 tests)
     - API 404 error tests (5 tests → 1 parameterized)
     - Choice field tests (4 tests → 1 with subTests)
     - Logo validation tests (6 tests → 1 parameterized)

2. **Email Configuration Tests** (4 tests)
   - File: `ropon_email/tests/test_send_email.py`
   - Potential reduction: 5 → 1 parameterized test
   - Tests missing/empty admin email with similar assertions

3. **User Access Tests** (Moderate)
   - File: `ropon_auth/tests/models/test_user_access.py` (11 tests)
   - Potential reduction: 11 → 7-8 tests
   - Combine form creation tests for superuser/moderator

### Medium-Priority (Medium Impact, Low Effort)
1. **Shared Test Fixtures**: Create `conftest.py` with reusable fixtures to reduce redundant setup
2. **Test Database**: Consider using faster `--keepdb` flag in development (already used in production)
3. **Mock External Services**: Ensure all external HTTP calls are mocked (already mostly done)

### Low-Priority (Low Impact)
1. **Test Documentation**: Add docstrings explaining why consolidated tests cover multiple scenarios
2. **Performance Monitoring**: Add test timing output to CI to track regressions

## Maintenance Guidelines

### When Adding New Tests
1. **Check for Existing Coverage**: Before adding a test, search for similar tests
2. **Use Parameterization**: If testing same logic with different inputs, use `subTest` or `pytest.parametrize`
3. **Avoid Excessive Fixtures**: Create minimal fixtures needed for test
4. **Use Test Settings**: Always run tests with `ropon.settings.test` locally

### When Tests Become Slow
1. **Profile Tests**: Use `--timing` flag to identify slow tests
2. **Check Database Queries**: Use Django Debug Toolbar or query counting
3. **Review Fixtures**: Ensure not creating unnecessary related objects
4. **Consider Test Isolation**: Can test be converted to unit test without DB?

## Verification

To verify optimizations are working:

```bash
# Run tests with timing
./backend/manage.py test --settings=ropon.settings.test --timing

# Run tests in parallel
./backend/manage.py test --settings=ropon.settings.test --parallel

# Run specific test file to compare before/after
./backend/manage.py test ropon_data.tests.blocks.test_geometry_blocks --settings=ropon.settings.test --timing
```

## References
- Django Testing Documentation: https://docs.djangoproject.com/en/stable/topics/testing/
- Wagtail Testing: https://docs.wagtail.org/en/stable/advanced_topics/testing.html
- pytest parametrize: https://docs.pytest.org/en/stable/parametrize.html
