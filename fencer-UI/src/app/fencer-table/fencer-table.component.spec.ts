import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FencerTableComponent } from './fencer-table.component';

describe('FencerTableComponent', () => {
  let component: FencerTableComponent;
  let fixture: ComponentFixture<FencerTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FencerTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FencerTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
