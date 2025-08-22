// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command to analyze a domain
Cypress.Commands.add('analyzeDomain', (domain) => {
  cy.get('#domain').clear().type(domain)
  cy.get('#analyze-btn').click()
  cy.wait('@analyzeRequest')
})

// Custom command to check for analysis results
Cypress.Commands.add('checkAnalysisResults', (domain) => {
  cy.contains('Analysis Results').should('be.visible')
  cy.contains(domain).should('be.visible')
})

// Custom command to check for error messages
Cypress.Commands.add('checkErrorMessage', (message) => {
  cy.contains(message).should('be.visible')
})

// Custom command to test responsive design
Cypress.Commands.add('testResponsive', () => {
  const sizes = [
    { width: 375, height: 667, name: 'Mobile' },
    { width: 768, height: 1024, name: 'Tablet' },
    { width: 1280, height: 720, name: 'Desktop' }
  ]
  
  sizes.forEach(size => {
    cy.viewport(size.width, size.height)
    cy.log(`Testing ${size.name} viewport: ${size.width}x${size.height}`)
    
    // Check that main elements are visible
    cy.get('#domain').should('be.visible')
    cy.get('#analyze-btn').should('be.visible')
  })
})

// Custom command to test BuiltWith search functionality
Cypress.Commands.add('testBuiltWithSearch', (searchTerm) => {
  cy.get('#tech-search').clear().type(searchTerm)
  cy.get('.tech-card-wrapper').should('have.length.gt', 0)
})

// Custom command to test Details toggle functionality
Cypress.Commands.add('testDetailsToggle', () => {
  cy.get('.details-toggle').first().click()
  cy.get('.variant-item').should('be.visible')
  cy.get('.details-toggle').first().click()
  cy.get('.variant-item').should('not.be.visible')
})

// Override visit command to add wait for page load
Cypress.Commands.overwrite('visit', (originalFn, url, options) => {
  return originalFn(url, {
    ...options,
    onBeforeLoad: (win) => {
      // Add any pre-load logic here
      if (options && options.onBeforeLoad) {
        options.onBeforeLoad(win)
      }
    }
  })
})