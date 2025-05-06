import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoawgComponent } from './poawg.component';

describe('PoawgComponent', () => {
  let component: PoawgComponent;
  let fixture: ComponentFixture<PoawgComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoawgComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PoawgComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
