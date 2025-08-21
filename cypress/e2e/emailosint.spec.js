/*
Purpose: To test the user flow and some data controls of the entire application as an E2E test.

Tests:
     Does the home page load?
     Does the form navigate to the second page after submission?
     Does the Back button work?
     Does the GitHub icon work correctly?

Is the API or JSON data correct (e.g., Kyiv JSON, BuiltWith API)?
*/

describe('EmailOSINT App End-to-End Tests', () => {

  beforeEach(() => {
    cy.visit('https://emailosint.onrender.com') // Ana sayfayı aç
  })

  it('Ana sayfa yükleniyor ve başlık doğru', () => {
    cy.contains('Email OSINT').should('be.visible')
  })

  it('İkinci sayfaya gidip back butonu çalışıyor', () => {
    cy.get('input[name="email"]').type('test@example.com')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/results') // ikinci sayfaya gidildiğini doğrula
    cy.get('button.back').click()          // back butonuna bas
    cy.url().should('eq', 'https://emailosint.onrender.com/') // ana sayfaya dönmeli
  })

  it('GitHub ikonu doğru çalışıyor', () => {
    cy.get('a.github-icon').should('have.attr', 'href').and('include', 'github.com')
  })

  it('Kiev JSON verisi doğru çalışıyor', () => {
    cy.get('#kiev-json').then($el => {
      const json = JSON.parse($el.text())
      expect(json).to.have.property('city', 'Kiev')
      expect(json).to.have.property('status', 'success')
    })
  })

  it('BuiltWith API doğru çalışıyor', () => {
    cy.get('#builtwith-result').then($el => {
      const data = JSON.parse($el.text())
      expect(data).to.have.property('technologies')
      expect(data.technologies).to.be.an('array')
    })
  })

})
