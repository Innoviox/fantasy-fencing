import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RocketShipComponent } from './rocket-ship/rocket-ship.component';
import { FencerTableComponent } from './fencer-table/fencer-table.component';

@NgModule({
  declarations: [
    AppComponent,
    RocketShipComponent,
    FencerTableComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
