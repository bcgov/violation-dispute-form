import { NgModule } from "@angular/core";
import { Routes, RouterModule } from "@angular/router";
import { SurveyPrimaryComponent } from "app/survey/primary.component";
import { SurveyResolver } from "app/survey/survey-resolver.service";
import { SurveyEditorComponent } from "app/survey/editor.component";
import { ContactComponent } from './contact/contact.component';
import { AuthGuard } from './guards/auth-guard.component';

const routes: Routes = [
  {
    path: "",
    component: SurveyPrimaryComponent,
    resolve: {
      // survey: SurveyResolver,
    },
    data: {
      breadcrumb: "Traffic Hearing Form",
      cache_name: "primary",
      survey_path: "assets/survey-primary.json",
  
    }
  },
  {
      path: "connect",
      component: ContactComponent,
      data: {
        breadcrumb: "Feedback"
      }
    },
  {
    path: "survey-editor",
    component: SurveyEditorComponent,
    canActivate: [AuthGuard],
    resolve: {
      // survey: SurveyResolver,
    },
    data: {
      role: "superuser",
      breadcrumb: "Survey Editor",
      cache_name: "editor",
      survey_path: "assets/survey-primary.json"
    }
  },
  {
    path: "sandbox",
    component: SurveyPrimaryComponent,
    canActivate: [AuthGuard],
    resolve: {
      // survey: SurveyResolver,
    },
    data: {
      role: "superuser",
      breadcrumb: "Survey Sandbox",
      survey_path: "assets/survey-sandbox.json"
    }
  },
  {
    path: "sandbox2",
    component: SurveyPrimaryComponent,
    canActivate: [AuthGuard],
    resolve: {
      // survey: SurveyResolver,
    },
    data: {
      role: "superuser",
      breadcrumb: "Survey Sandbox 2",
      survey_path: "assets/survey-sandbox-2.json"
    }
  },
  {
    path: "sandbox3",
    component: SurveyPrimaryComponent,
    canActivate: [AuthGuard],
    resolve: {
      // survey: SurveyResolver,
    },
    data: {
      role: "superuser",
      breadcrumb: "Survey Sandbox 3",
      survey_path: "assets/survey-sandbox-3.json"
    }
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: [SurveyResolver]
})
export class AppRoutingModule {}
