import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import {
  HttpClientModule,
  HttpClientXsrfModule,
  HTTP_INTERCEPTORS
} from "@angular/common/http";
import { HttpCsrfInterceptor } from "./csrf-interceptor.provider";
import { MatomoModule } from "@ambroise-rabier/ngx-matomo";

import { AppRoutingModule } from "./app-routing.module";

import { AppComponent } from "./app.component";
import { SearchBoxDirective } from "./search-box/search-box.directive";
import { GeneralDataService } from "app/general-data.service";
import { AdminModule } from "app/admin/admin.module";
import { BreadcrumbComponent } from "./breadcrumb/breadcrumb.component";
import { GlossaryService } from "./glossary/glossary.service";
import { GlossaryEditorComponent } from "./glossary/editor.component";
import { InsertComponent } from "./insert/insert.component";
import { InsertService } from "./insert/insert.service";
import { StaticComponent } from "./static/static.component";
import { SurveyComponent } from "./survey/survey.component";
import { SurveyPrimaryComponent } from "./survey/primary.component";
import { SurveyEditorComponent } from "./survey/editor.component";
import { RecaptchaModule, RecaptchaFormsModule } from 'ng-recaptcha';
import { AdminDataService } from "./admin/admin-data.service";
import { AuthGuard } from "./guards/auth-guard.component"
import { ContactComponent } from './contact/contact.component';

@NgModule({
  declarations: [
    AppComponent,
    SearchBoxDirective,
    BreadcrumbComponent,
    GlossaryEditorComponent,
    InsertComponent,
    SurveyComponent,
    SurveyPrimaryComponent,
    SurveyEditorComponent,
    ContactComponent,
    StaticComponent
  ],
  imports: [
    BrowserModule,
    RecaptchaModule,
    RecaptchaFormsModule,
    FormsModule,
    HttpClientModule,
    HttpClientXsrfModule.withOptions({
      cookieName: "csrftoken",
      headerName: "X-CSRFToken"
    }),
    AppRoutingModule,
    AdminModule,
    MatomoModule
  ],
  providers: [
    GeneralDataService,
    GlossaryService,
    InsertService,
    AdminDataService,
    { provide: HTTP_INTERCEPTORS, useClass: HttpCsrfInterceptor, multi: true },
    AuthGuard,
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
