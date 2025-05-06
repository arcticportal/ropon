import { TestBed } from '@angular/core/testing';

import { CachedHttpService } from './cached-http.service';

describe('CachedHttpService', () => {
  let service: CachedHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CachedHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
