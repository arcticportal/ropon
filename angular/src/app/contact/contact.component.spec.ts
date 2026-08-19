import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting
} from '@angular/common/http/testing';

import { ContactComponent } from './contact.component';
import { environment } from '../../environments/environment';

describe('ContactComponent', () => {
  let component: ContactComponent;
  let fixture: ComponentFixture<ContactComponent>;
  let httpMock: HttpTestingController;

  // Must stay in sync with the component's honeypotCandidates list.
  const honeypotCandidates = ['fax_number', 'web_address2', 'contact_ref', 'alt_phone2', 'org_ref', 'site_link2'];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContactComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContactComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('registers the honeypot control under one of the candidate names', () => {
    expect(honeypotCandidates).toContain(component.honeypotField);
    expect(component.contactForm.get(component.honeypotField)).toBeTruthy();
  });

  it('clears the honeypot control when a browser autofill animation fires on it', () => {
    const honeypotControl = component.contactForm.get(component.honeypotField)!;
    honeypotControl.setValue('autofilled-by-browser');

    const event = new AnimationEvent('animationstart', { animationName: 'onAutoFillStart' });
    Object.defineProperty(event, 'target', {
      value: { id: component.honeypotField }
    });
    component.onAutoFillStart(event);

    expect(honeypotControl.value).toBe('');
  });

  it('ignores animationstart events that are not the autofill tripwire', () => {
    const honeypotControl = component.contactForm.get(component.honeypotField)!;
    honeypotControl.setValue('kept');

    const wrongName = new AnimationEvent('animationstart', { animationName: 'somethingElse' });
    Object.defineProperty(wrongName, 'target', {
      value: { id: component.honeypotField }
    });
    component.onAutoFillStart(wrongName);

    const wrongTarget = new AnimationEvent('animationstart', { animationName: 'onAutoFillStart' });
    Object.defineProperty(wrongTarget, 'target', { value: { id: 'name' } });
    component.onAutoFillStart(wrongTarget);

    expect(honeypotControl.value).toBe('kept');
  });

  it('omits the honeypot key from the payload when the input matches the autofill pseudo-class', () => {
    // Fill the visible fields so the form is valid.
    component.contactForm.patchValue({
      name: 'Real User',
      from_email_id: 'real@example.org',
      message: 'A genuinely typed message.'
    });
    component.contactForm.get(component.honeypotField)!.setValue('autofilled');

    // Simulate the browser autofill signature on the honeypot element.
    const honeypotEl = document.getElementById(component.honeypotField)!;
    spyOn(honeypotEl, 'matches').and.returnValue(true);

    component.onSubmit();

    const req = httpMock.expectOne(environment.backendURL + '/api/v2/email/contact-us/');
    expect(req.request.body[component.honeypotField]).toBeUndefined();
    expect(req.request.body.name).toBe('Real User');
    req.flush({});
  });

  it('tolerates browsers where a vendor autofill pseudo-class is unsupported', () => {
    // Regression: probing ':autofill, :-webkit-autofill, :-moz-autofill' as
    // one selector list throws in Chrome (unknown :-moz-autofill) and left
    // the form stuck at "Sending". Each probe must fail isolated.
    component.contactForm.patchValue({
      name: 'Real User',
      from_email_id: 'real@example.org',
      message: 'A genuinely typed message.'
    });
    component.contactForm.get(component.honeypotField)!.setValue('autofilled');

    const honeypotEl = document.getElementById(component.honeypotField)!;
    // Simulate Chrome: unknown pseudo-classes throw, the supported one matches.
    spyOn(honeypotEl, 'matches').and.callFake((selector: string) => {
      if (selector === ':-moz-autofill') {
        throw new SyntaxError(`'${selector}' is not a valid selector`);
      }
      return selector === ':-webkit-autofill';
    });

    component.onSubmit();

    const req = httpMock.expectOne(environment.backendURL + '/api/v2/email/contact-us/');
    expect(req.request.body[component.honeypotField]).toBeUndefined();
    req.flush({});
    expect(component.submissionState).toBe('success');
  });

  it('keeps a script-filled honeypot in the payload when there is no autofill signature', () => {
    // Bots fill fields via script: the :-webkit-autofill pseudo-class never
    // matches, so the trap value must still reach the backend.
    component.contactForm.patchValue({
      name: 'Bot',
      from_email_id: 'bot@example.org',
      message: 'Spammy spam spam spam.'
    });
    component.contactForm.get(component.honeypotField)!.setValue('https://spam.example');

    const honeypotEl = document.getElementById(component.honeypotField)!;
    spyOn(honeypotEl, 'matches').and.returnValue(false);

    component.onSubmit();

    const req = httpMock.expectOne(environment.backendURL + '/api/v2/email/contact-us/');
    expect(req.request.body[component.honeypotField]).toBe('https://spam.example');
    req.flush({});
  });
});
