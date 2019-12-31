import { TestBed } from '@angular/core/testing';

import { FencerService } from './fencer.service';

describe('FencerService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: FencerService = TestBed.get(FencerService);
    expect(service).toBeTruthy();
  });
});
